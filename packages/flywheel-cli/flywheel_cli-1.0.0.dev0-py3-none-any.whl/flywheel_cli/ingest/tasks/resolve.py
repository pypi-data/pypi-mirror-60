"""Provides ResolveTask class."""

import logging

import fs

from ... import util
from ..container_factory import ContainerFactory
from .. import schemas
from .abstract import AbstractTask

log = logging.getLogger(__name__)


class ResolveTask(AbstractTask):
    """Resolve containers for review."""

    def _execute(self):
        container_factory = ContainerFactory(self.fw)
        # build container hierarchy from item context
        for item in self.ingest_db.get_items():
            container = container_factory.resolve(item.context)

        # walk through the containers and insert them into the db
        for parent, container in container_factory.walk_containers():
            self.ingest_db.create_container(schemas.ContainerIn(
                id=container.id,
                level=container.level,
                src_context=container.src_context,
                dst_context=container.dst_context,
                dst_path=container.get_dst_path(),
                parent_id=parent.id if parent else None,
            ))

        # update items with container info
        for item in self.ingest_db.get_items():
            container = container_factory.resolve(item.context)
            if not container:
                log.warning(f"Couldn't resolve container for: {item.path}")
                continue
            filename = item.filename or self._get_filename(item, container.dst_context)
            update = {
                "container_id": container.id,
                "existing": filename in container.dst_files,
            }
            if filename != item.filename:
                update["filename"] = filename
            # update item
            self.ingest_db.update_item(item.id, **update)

    def _after_complete(self):
        self.ingest_db.set_ingest_status(status=schemas.IngestStatus.in_review)
        if self.config.assume_yes:
            # ingest was started with assume yes so accept the review
            self.ingest_db.review_ingest()

    def _after_failed(self):
        self.ingest_db.fail_ingest()

    @staticmethod
    def _get_filename(item, dst_context):
        if item.type == schemas.ItemType.packfile:
            packfile_name = util.str_to_filename(dst_context.get("label"))
            if dst_context["packfile"]["type"] == "zip":
                filename = f"{packfile_name}.zip"
            else:
                filename = f"{packfile_name}.{dst_context['packfile']['type']}.zip"
        else:
            filename = fs.path.basename(item.files[0])
        return filename
