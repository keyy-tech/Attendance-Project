from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet,
    PermissionRequestViewSet,
    rfid_check_in,
    finalize_session_qr,
    create_permission,
    close_session,
)

router = DefaultRouter()
router.register(r"records", AttendanceViewSet, basename="attendance-records")
router.register(
    r"permissions", PermissionRequestViewSet, basename="permission-requests"
)

urlpatterns = [
    path("rfid-check-in/", rfid_check_in, name="rfid-check-in"),
    path("finalize-session/", finalize_session_qr, name="finalize-session-qr"),
    path("permission/", create_permission, name="create-permission"),
    path("close-session/", close_session, name="close-session"),
]

urlpatterns += router.urls
