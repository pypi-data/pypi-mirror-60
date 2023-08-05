"""Provides PrepareTask class."""
import logging

from ..container_factory import ContainerFactory
from .. import schemas
from .abstract import AbstractTask

log = logging.getLogger(__name__)


class PrepareTask(AbstractTask):
    """Preprocessing work."""

    def _execute(self):
        """Process review, create and enqueue upload tasks"""
        container_factory = ContainerFactory(self.fw)

        # build hierarchy
        for container in self.ingest_db.get_containers():
            container_factory.add_node(
                container.id,
                container.parent_id,
                container.level,
                src_context=container.src_context,
                dst_context=container.dst_context,
            )
        # create missing containers
        created_containers = container_factory.create_containers()
        # update dst_context on newly created containers
        for container in created_containers:
            self.ingest_db.update_container(
                container.id,
                dst_context=container.dst_context,
                dst_path=container.get_dst_path(),
            )

        self.ingest_db.set_ingest_status(status=schemas.IngestStatus.uploading)
        for item in self.ingest_db.get_items():
            if self.config.skip_existing and item.existing:
                self.ingest_db.update_item(
                    item_id=item.id,
                    skipped=True,
                )
                log.debug(f"Skipped item {item.id} because it already exists")
                continue
            self.ingest_db.create_task(schemas.TaskIn(
                type=schemas.TaskType.upload,
                item_id=item.id,
            ))

    def _after_complete(self):
        # possible that no upload tasks were created - finalize
        self.ingest_db.finalize_ingest_after_upload()

    def _after_failed(self):
        self.ingest_db.fail_ingest()
