from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Course, TimeTable, ClassSession
from .serializers import (
    CourseSerializer,
    TimeTableSerializer,
    ClassSessionSerializer,
    CreateAdhocSessionSerializer,
    SessionQRActivateSerializer,
    SessionQRDeactivateSerializer,
    SessionCancelSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("code")
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


class TimeTableViewSet(viewsets.ModelViewSet):
    queryset = TimeTable.objects.select_related("course", "lecturer").all()
    serializer_class = TimeTableSerializer
    permission_classes = [permissions.AllowAny]


class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.select_related(
        "course", "lecturer", "timetable"
    ).all()
    serializer_class = ClassSessionSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_adhoc_session(request):
    """
    Lecturer creates a one-off (fixed) class session.
    """
    s = CreateAdhocSessionSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    session = s.save()
    return Response(
        ClassSessionSerializer(session).data, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def activate_qr(request):
    """
    Activate QR double-check for a session (generates token if missing).
    body: { "session_id": <int> }
    """
    s = SessionQRActivateSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    session = s.save()
    return Response(
        {
            "message": "QR activated.",
            "session_id": session.id,
            "qr_active": session.qr_active,
            "require_qr_verification": session.require_qr_verification,
            "session_qr_token": session.session_qr_token,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def deactivate_qr(request):
    """
    Deactivate QR double-check for a session.
    body: { "session_id": <int> }
    """
    s = SessionQRDeactivateSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    session = s.save()
    return Response(
        {
            "message": "QR deactivated.",
            "session_id": session.id,
            "qr_active": session.qr_active,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def cancel_session(request):
    """
    Cancel a class session—attendance will be blocked.
    body: { "session_id": <int> }
    """
    s = SessionCancelSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    session = s.save()
    return Response(
        {
            "message": "Session cancelled.",
            "session_id": session.id,
            "is_cancelled": session.is_cancelled,
        },
        status=200,
    )
