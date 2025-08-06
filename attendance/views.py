from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Attendance, PermissionRequest
from .serializers import (
    AttendanceSerializer,
    PermissionRequestCreateSerializer,
    RFIDCheckInSerializer,
    FinalizeSessionQRSerializer,
    CloseSessionSerializer,
)


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only listing/detail for attendance records.
    Creation happens through workflow endpoints (RFID/QR/Permission), not direct POST.
    """

    queryset = Attendance.objects.select_related(
        "student", "session", "session__course", "session__lecturer"
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.AllowAny]


class PermissionRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only; creating permissions is via the dedicated endpoint below.
    """

    queryset = PermissionRequest.objects.select_related("student", "session").all()
    serializer_class = PermissionRequestCreateSerializer  # returns basic fields
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def rfid_check_in(request):
    """
    Step 1: RFID check-in (or index number) within the attendance window.
    body: { rfid_tag?: str, index_number?: str, session_id: int }
    """
    s = RFIDCheckInSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    att = s.save()
    return Response(
        {
            "message": "RFID recorded.",
            "pending_qr": not att.is_verified,
            "attendance": AttendanceSerializer(att).data,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def finalize_session_qr(request):
    """
    Step 2: Finalize attendance using session QR token + index number.
    body: { session_token: str, index_number: str }
    """
    s = FinalizeSessionQRSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    att = s.save()
    return Response(
        {
            "message": "Attendance finalized via QR.",
            "attendance": AttendanceSerializer(att).data,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # tighten to lecturers only
def create_permission(request):
    """
    Lecturer grants an excuse; attendance becomes EXCUSED immediately.
    body: { student_id: int, session_id: int, reason?: str }
    """
    s = PermissionRequestCreateSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    perm = s.save()
    # fetch updated attendance to return
    att = Attendance.objects.get(student=perm.student, session=perm.session)
    return Response(
        {
            "message": "Permission recorded and attendance marked EXCUSED.",
            "permission": {
                "id": perm.id,
                "student_id": perm.student_id,
                "session_id": perm.session_id,
                "reason": perm.reason,
                "created_at": perm.created_at,
            },
            "attendance": AttendanceSerializer(att).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def close_session(request):
    """
    End-of-class helper: currently disables QR for the session.
    body: { session_id: int }
    """
    s = CloseSessionSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    session = s.save()
    return Response(
        {
            "message": "Session closed.",
            "session_id": session.id,
            "qr_active": session.qr_active,
        },
        status=200,
    )
