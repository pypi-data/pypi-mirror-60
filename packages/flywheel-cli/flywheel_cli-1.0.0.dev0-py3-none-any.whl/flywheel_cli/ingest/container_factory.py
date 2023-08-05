"""Provides interface for container creation"""
import collections
import copy
import logging
import sys
import uuid

import crayons
import fs
import flywheel

from . import schemas

CONTAINERS = ["group", "project", "subject", "session", "acquisition"]
CONTAINER_FIELDS = ["id", "label", "uid", "code"]

log = logging.getLogger(__name__)


def path_el(c_type, context, reverse=False):
    """Get the path element for container"""
    if c_type == "group":
        return context.get("_id")
    priority_order = ["_id", "label"]
    if reverse:
        # prefer label
        priority_order = reversed(priority_order)
    for field in priority_order:
        value = context.get(field)
        if not value:
            continue
        if field == "_id":
            return f"<id:{value}>"
        if field == "label":
            return f"{value}"
    log.error(f"Could not determine {c_type}")
    raise Exception("Not enough information to determine container")

class ContainerNode:
    """Represents a container node in the hierarchy"""

    # pylint: disable=bad-continuation, too-few-public-methods, too-many-arguments
    def __init__(
        self,
        level,
        id_=None,
        parent=None,
        src_context=None,
        dst_context=None,
        dst_files=None,
        exists=False,
        bytes_sum=None,
        files_cnt=None,
    ):
        """Initialize ContainerNode"""
        self.id = id_ or uuid.uuid4()  # pylint: disable=invalid-name
        self.level = level
        self.parent = parent
        self.src_context = src_context
        self.dst_context = dst_context
        self.dst_files = dst_files or []
        self.exists = exists or dst_context
        self.children = []
        self.bytes_sum = bytes_sum or 0
        self.files_cnt = files_cnt or 0

    def get_dst_path(self):
        """Get human friendly representation of destination"""
        if not self.dst_context:
            # no destination context
            return None
        parts = []
        current = self
        while current.level != "root":
            parts.append(
                path_el(current.level.name, current.dst_context, reverse=True)
            )
            current = current.parent
        return "/".join(reversed(parts))

    def __str__(self):
        context = self.dst_context or self.src_context
        label = context.get("label") or context.get("_id") or "NO_LABEL"
        filesize = fs.filesize.traditional(self.bytes_sum)
        plural = "s" if self.files_cnt > 1 else ""
        status = "using" if self.exists else "creating"
        parts = [f"{crayons.blue(label)}"]
        if self.bytes_sum and self.files_cnt:  # container w/ files
            parts.append(f"({filesize} / {self.files_cnt} file{plural})")
        elif self.bytes_sum:  # file
            parts.append(f"({filesize})")
        parts.append(f"({status})")
        return " ".join(parts)


class ContainerFactory:
    """Container factory class"""

    def __init__(self, fw=None):
        """Manages discovery and creation of containers by looking at context objects."""
        self.fw = fw

        # The root container
        self.root = ContainerNode("root", exists=True)
        self.nodes = {
            self.root.id: self.root,
        }

    def resolve(self, context):
        """Add node from context"""
        prev = self.root
        path = ""
        for container in CONTAINERS:
            if container in context:
                path = fs.path.combine(path, path_el(container, context[container]))
                current = self._resolve_child(prev, container, path, context[container])
                if current is None:
                    return None
                prev = current
        return prev

    def add_node(self, id_, parent, level, **kwargs):
        """Rebuild the hierarchy by adding nodes one by one."""
        if id_ in self.nodes:
            return
        node = ContainerNode(id_=id_, level=level, **kwargs)
        self.nodes[node.id] = node
        parent_node = self.nodes[parent] if parent else self.root
        parent_node.children.append(node)
        node.parent = parent_node
        # populate size to parents
        current = parent_node
        while current:
            current.bytes_sum += node.bytes_sum
            current = current.parent
        # track total file count on root node
        self.root.files_cnt += node.files_cnt

    def create_containers(self):
        """Create non existent container in Flywheel."""
        created_containers = []
        for parent, child in self.walk_containers():
            if not child.exists:
                self._create_container(parent, child)
                child.exists = True
                created_containers.append(child)
        return created_containers

    def walk_containers(self):
        """Breadth-first walk of containers resolved by this factory

        Yields:
            ContainerNode, ContainerNode: parent, child container nodes
        """
        queue = collections.deque()
        for child in self.root.children:
            queue.append((None, child))

        while queue:
            parent, current = queue.popleft()

            for child in current.children:
                queue.append((current, child))
            # skip root container
            if current.id == "root":
                continue
            yield parent, current

    def get_first_project(self):
        """Get the first project in the hierarchy.

        Returns:
            ContainerNode: The first project node, or None
        """
        groups = self.root.children
        if not groups:
            return None
        projects = groups[0].children
        if not projects:
            return None
        return projects[0]

    def print_tree(self, fs_url="/", fh=sys.stdout):
        """Print hierarchy"""
        utf8 = fh.encoding == "UTF-8"
        none_str = "│  " if utf8 else "|  "
        node_str = "├─ " if utf8 else "|- "
        last_str = "└─ " if utf8 else "`- "

        def pprint_tree(node, prefix="", last=True):
            print(prefix, last_str if last else node_str, node, file=fh, sep="")
            prefix += "   " if last else none_str
            child_count = len(node.children)
            children = node.children
            for i, child in enumerate(children):
                last = i == (child_count - 1)
                pprint_tree(child, prefix, last)

        size_str = fs.filesize.traditional(self.root.bytes_sum)
        fh.write(f"{fs_url} ({size_str} / {self.root.files_cnt} files)".ljust(80))
        fh.write("\n")
        fh.flush()
        for child in self.root.children:
            pprint_tree(child)

    def _resolve_child(self, parent, level, path, context):
        """Resolve a child"""
        cid = context.get("_id")
        # uid = context.get("uid")
        label = context.get("label")

        for child in parent.children:
            # Prefer resolve by id
            if cid and child.src_context.get("_id") == cid:
                return child

            if cid:
                continue

            if label and child.src_context.get("label") == label:
                return child

        # Create child
        child = ContainerNode(
            schemas.ContainerLevel[level], parent=parent, src_context=context
        )

        if parent.exists:
            target, dst_files = None, None

            if cid:
                target, dst_files = self._find_child_by_path(level, path)
            elif label and not target:
                # lastly start resolve by label
                target, dst_files = self._find_child_by_path(level, path)

            if target:
                child.exists = True
                child.dst_context = self._get_dst_context(target)
                child.dst_files = dst_files

        parent.children.append(child)
        self.nodes[child.id] = child
        return child

    def _find_child_by_path(self, container_type, path):
        """Attempt to find the child."""
        try:
            result = self.fw.resolve(fs.path.combine(path, "files"))
            container = result.path[-1]
            files = list(map(lambda f: f.name, result.children))
            log.debug(f"Resolve {container_type}: {path} - returned: {container.id}")
            return container, files
        except flywheel.ApiException:
            log.debug(f"Resolve {container_type}: {path} - NOT FOUND")
            return None, None

    def _create_container(self, parent, node):
        create_fn = getattr(self.fw, f"add_{node.level.name}", None)
        if not create_fn:
            raise ValueError(f"Unsupported container type: {node.level.name}")
        create_doc = copy.deepcopy(node.src_context)
        if node.level.name == "session":
            # Add subject to session
            create_doc["project"] = parent.parent.dst_context["_id"]
            create_doc["subject"] = {"_id": parent.dst_context["_id"]}
        elif parent:
            create_doc[parent.level.name] = parent.dst_context["_id"]
        if node.level.name == "subject":
            create_doc.setdefault("code", create_doc.get("label"))
        new_id = create_fn(create_doc)
        log.debug(f"Created container: {create_doc} as {new_id}")
        get_fn = getattr(self.fw, f"get_{node.level.name}", None)
        target = get_fn(new_id)
        node.dst_context = self._get_dst_context(target)
        return new_id

    @staticmethod
    def _get_dst_context(container):
        """Get metadata from flywheel container object returned by sdk."""
        src = container.to_dict()
        ctx = {key: src.get(key) for key in CONTAINER_FIELDS if src.get(key)}
        ctx["_id"] = ctx.pop("id")
        return ctx
