import json

from django.apps import apps
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.forms.models import ModelForm
from django.http import Http404, JsonResponse
from django.utils.text import slugify

from ink_cms.config import INK_CONFIG
from ink_cms.forms import ArticleForm, BlogEntryForm, PageForm
from ink_cms.models import Revision, SiteSection


class InkAdmin(admin.ModelAdmin):
    change_form_template = "ink_cms/application.html"

    def __init__(self, model, site, **kwargs):
        if self.form == ModelForm:
            # Form wasn't changed by user; use Ink defaults
            INK_FORMS = {
                "Article": ArticleForm,
                "BlogEntry": BlogEntryForm,
                "Page": PageForm,
            }
            self.form = INK_FORMS[model.__name__]
        return super().__init__(model, site, **kwargs)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        if request.method == "POST":
            data = json.loads(request.body)
            action = data.get("_cms_action")
            if action:
                del data["_cms_action"]
            if action == "save":
                return self.handle_save(data, object_id, request)
            elif action == "publish":
                return self.handle_publish(data, object_id, request)
        elif request.method == "GET" and request.GET.get("format") == "json":
            content_type = ContentType.objects.get_for_model(self.model)
            latest = (
                Revision.objects.filter(object_id=object_id, content_type=content_type)
                .order_by("-date_created")
                .first()
            )
            return JsonResponse(latest.data)

        return super()._changeform_view(request, object_id, form_url, extra_context)

    def handle_save(self, data, object_id, request):
        change = bool(object_id)
        if change:
            try:
                obj = self.model.objects.get(id=object_id)
            except self.model.DoesNotExist:
                raise Http404()
            if not self.has_change_permission(request, obj):
                raise PermissionDenied
        else:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None
            data["created_by"] = request.user

        # Process data
        data["slug"] = data.get("slug") or slugify(data.get("title", ""))

        ModelForm = self.get_form(request, change=change)
        form = ModelForm(data, request.FILES, instance=obj)

        # Create and validate form and JSON response
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)
        obj = form.save()

        # Exclude some fields from saving to the Revision
        excluded_fields = [
            "created_by",  # Doesn't change, so doesn't need to be stored
            "published_content",  # Available as most recent revision
        ]
        for field in excluded_fields:
            if data.get(field):
                del data[field]
        data["id"] = obj.id
        Revision.objects.create(obj=obj, data=data, user=request.user)
        if change:
            return JsonResponse(
                {
                    "messages": [{"type": "success", "content": "Save successful"}],
                    "id": obj.id,
                }
            )
        else:
            return JsonResponse({"id": obj.id}, status=201)

    def handle_publish(self, data, object_id, request):
        try:
            obj = self.model.objects.get(id=object_id)
        except self.model.DoesNotExist:
            raise Http404()
        data["published_content"] = getattr(obj, "published_content", {})
        raise NotImplementedError()


class InkDevAdmin(InkAdmin):
    """Development utility for Ink

    This class is used when `INK_CONFIG["DEV"]` is set to `True`.

    If you're developing functionality for Ink, thank you!
    If you're not, you probably don't need to worry about this class, and either
    unset `INK_CONFIG["DEV"]` or set `False` as its value.
    """

    change_form_template = "ink_cms/dev_application.html"


if INK_CONFIG["DEV"] is True:
    active_admin_class = InkDevAdmin
else:
    active_admin_class = InkAdmin

for model_name in INK_CONFIG["CONTENT_MODELS"]:
    model = apps.get_model(model_name)
    admin.site.register(model, active_admin_class)

# Support models
@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    pass
