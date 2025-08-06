from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, LecturerViewSet

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"lecturers", LecturerViewSet, basename="lecturers")

urlpatterns = router.urls
