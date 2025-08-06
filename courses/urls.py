from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    TimeTableViewSet,
    ClassSessionViewSet,
    create_adhoc_session,
    activate_qr,
    deactivate_qr,
    cancel_session,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"timetable", TimeTableViewSet, basename="timetable")
router.register(r"sessions", ClassSessionViewSet, basename="sessions")

urlpatterns = [
    path("sessions/adhoc/", create_adhoc_session, name="create-adhoc-session"),
    path("sessions/qr/activate/", activate_qr, name="activate-qr"),
    path("sessions/qr/deactivate/", deactivate_qr, name="deactivate-qr"),
    path("sessions/cancel/", cancel_session, name="cancel-session"),
]

