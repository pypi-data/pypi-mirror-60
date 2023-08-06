from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

from ink_cms.image import get_datestamped_upload_path


class SharedInkAbstractModel(models.Model):
    """Abstract model parent shared by all Ink CMS content types."""

    published_content = JSONField(
        default=dict, encoder=DjangoJSONEncoder, blank=True, null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    slug = models.CharField(max_length=255, db_index=True, unique=True)
    title = models.CharField(max_length=511, unique=True)
    workflowstate = models.CharField(
        default="draft",
        max_length=15,
        choices=(
            ("draft", "Draft"),
            ("published", "Published"),
            ("modified", "Published with later modifications"),
        ),
        db_index=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Article(SharedInkAbstractModel):
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"


class BlogEntry(SharedInkAbstractModel):
    class Meta:
        verbose_name = "Blog Entry"
        verbose_name_plural = "Blog Entries"


class Page(SharedInkAbstractModel):
    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"


# #############
# Uploaded Content
# #############


class UploadedImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey("content_type", "object_id")
    image = ThumbnailerImageField(
        blank=True, null=True, upload_to=get_datestamped_upload_path
    )


# #############
# Taxonomy
# #############
class AbstractTaxonomy(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class SiteSection(AbstractTaxonomy):
    class Meta:
        ordering = ["name"]
        verbose_name = "Site Section"
        verbose_name_plural = "Site Sections"


class Tag(AbstractTaxonomy):
    class Meta:
        ordering = ["name"]


# #############
# Revision History
# #############


class Revision(models.Model):
    data = JSONField()
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey("content_type", "object_id")

    class Meta:
        index_together = [["content_type", "object_id", "date_created"]]
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.obj} version from {self.date_created.strftime('c')}"
