from django.db import models
from django.utils import timezone


class ModelCreatedAtMixin(models.Model):
    """
    Mixin class for created_at model field.
    """
    created_at = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        abstract = True


class ModelTimeStampMixin(ModelCreatedAtMixin):
    """
    Mixin class for created_at and updated_at model fields.
    """
    updated_at = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        abstract = True
