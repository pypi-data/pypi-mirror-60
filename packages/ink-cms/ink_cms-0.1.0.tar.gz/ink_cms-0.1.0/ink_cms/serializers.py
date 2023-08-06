import os

from django.conf import settings
from django.contrib.auth import get_user_model
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from ink_cms.config import INK_CONFIG
from ink_cms.models import Revision, SiteSection, Tag


# Taxonomy
class SharedTaxonomySerializer(serializers.ModelSerializer):
    pass


class SiteSectionSerializer(SharedTaxonomySerializer):
    class Meta:
        fields = "__all__"
        model = SiteSection


class TagSerializer(SharedTaxonomySerializer):
    class Meta:
        fields = "__all__"
        model = Tag


# Editor
class StaffSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        exclude = [
            "date_joined",
            "is_superuser",
            "groups",
            "last_login",
            "password",
            "user_permissions",
        ]
        model = get_user_model()

    def get_display_name(self, obj):
        return getattr(obj, INK_CONFIG["USERNAME_DISPLAY"])()


class RevisionSerializer(serializers.ModelSerializer):
    user = StaffSerializer(read_only=True)

    class Meta:
        fields = "__all__"
        model = Revision


class ImageSerializer(serializers.Serializer):
    filename = serializers.SerializerMethodField()
    optimized = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    def photo_option(self, obj, option_name):
        if not obj:
            return None
        option = INK_CONFIG["THUMBNAIL_ALIASES"][""][option_name]
        filepath = get_thumbnailer(obj).get_thumbnail(option).url
        return os.path.join(settings.MEDIA_URL, filepath)

    def get_filename(self, obj):
        return obj.name.rsplit("/", 1)[1]

    def get_optimized(self, obj):
        return self.photo_option(obj, "optimized")

    def get_thumbnail(self, obj):
        return self.photo_option(obj, "thumbnail")
