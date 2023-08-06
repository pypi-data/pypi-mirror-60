from rest_framework import routers

from ink_cms.views import RevisionViewSet, StaffViewSet, SiteSectionViewSet, TagViewSet

router = routers.DefaultRouter()
router.register("revisions", RevisionViewSet)
router.register("staff", StaffViewSet)
router.register("site_sections", SiteSectionViewSet)
router.register("tags", TagViewSet)
