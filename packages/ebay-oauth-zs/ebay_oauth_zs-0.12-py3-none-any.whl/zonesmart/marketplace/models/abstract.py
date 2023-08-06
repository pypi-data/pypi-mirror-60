from model_utils import Choices
from model_utils.fields import (
    AutoCreatedField,
    AutoLastModifiedField,
    MonitorField,
    StatusField,
)

from zonesmart.models import UUIDModel


class MarketplaceEntity(UUIDModel):
    created = AutoCreatedField()
    modified = AutoLastModifiedField()

    STATUS = Choices("draft", "ready_to_publish", "published", "update_required")
    status = StatusField(default="draft")

    published_at = MonitorField(monitor="status", when=["published"])

    REQUIRED_FOR_PUBLISHING_FIELDS = []
    TRACKER_EXCLUDE_FIELDS = ["status"]

    class Meta:
        abstract = True

    def extra_check_if_ready_for_publishing(self):
        return True

    @property
    def ready_to_be_published(self):
        for field in self.REQUIRED_FOR_PUBLISHING_FIELDS:
            if not hasattr(self, field):
                return False
        return self.extra_check_if_ready_for_publishing()

    @property
    def update_needed(self):
        return self.modified > self.published_at

    @property
    def published(self):
        return self.status == self.STATUS.published

    @published.setter
    def published(self, value: bool):
        if value:
            self.status = self.STATUS.published
        else:
            self.status = (
                self.STATUS.ready_to_publish
                if self.ready_to_be_published
                else self.STATUS.draft
            )

    def save(self, *args, **kwargs):
        if self.ready_to_be_published:
            if self.status not in [self.STATUS.published, self.STATUS.update_required]:
                self.status = self.STATUS.ready_to_publish
            elif getattr(self, "tracker", None) and self.STATUS.published:
                changed_fields = self.tracker.changed()
                for (
                    field
                ) in self.TRACKER_EXCLUDE_FIELDS:  # pop fields from updated fields
                    changed_fields.pop(field, None)
                if changed_fields:
                    self.status = self.STATUS.update_required
        super().save(*args, **kwargs)
