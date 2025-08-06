from rest_framework import serializers
from django.utils import timezone
from .models import Attendance, PermissionRequest
from users.models import Student
from users.serializers import StudentSerializer
from courses.models import ClassSession
from courses.serializers import ClassSessionSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student", write_only=True
    )
    session = ClassSessionSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassSession.objects.all(), source="session", write_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id", "student", "student_id", "session", "session_id",
            "check_in_time", "verification_method", "status",
            "marks_awarded", "is_verified", "qr_token", "created_at"
        ]
        read_only_fields = ["created_at", "qr_token"]


# --------- Workflow serializers for Attendance ---------

class RFIDCheckInSerializer(serializers.Serializer):
    rfid_tag = serializers.CharField(required=False, allow_blank=True)
    index_number = serializers.CharField(required=False, allow_blank=True)
    session_id = serializers.IntegerField()

    def validate(self, data):
        if not data.get("rfid_tag") and not data.get("index_number"):
            raise serializers.ValidationError("Provide either rfid_tag or index_number.")

        # Student
        try:
            if data.get("rfid_tag"):
                student = Student.objects.get(rfid_tag=data["rfid_tag"], is_active=True)
            else:
                student = Student.objects.get(index_number=data["index_number"], is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found or inactive.")
        data["student"] = student

        # Session
        try:
            session = ClassSession.objects.get(pk=data["session_id"])
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("Session not found.")
        if session.is_cancelled:
            raise serializers.ValidationError("Session is cancelled.")
        if not session.is_within_attendance_window():
            raise serializers.ValidationError("Attendance window is closed.")
        data["session"] = session
        return data

    def create(self, validated):
        student = validated["student"]
        session = validated["session"]
        now = timezone.now()
        pending_qr = bool(session.qr_active)

        att, _ = Attendance.objects.get_or_create(
            student=student, session=session,
            defaults={
                "status": "PRESENT",
                "verification_method": "RFID",
                "check_in_time": now,
                "is_verified": not pending_qr,
            }
        )
        # Update if it already existed
        att.status = "PRESENT"
        att.verification_method = "RFID"
        att.check_in_time = att.check_in_time or now
        att.is_verified = not pending_qr
        att.save()
        return att


class FinalizeSessionQRSerializer(serializers.Serializer):
    session_token = serializers.CharField()
    index_number = serializers.CharField()

    def validate(self, data):
        # Session by token and must be active (or allow grace if preferred)
        try:
            session = ClassSession.objects.get(session_qr_token=data["session_token"], is_cancelled=False)
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive session token.")

        if not session.qr_active:
            raise serializers.ValidationError("QR verification is not active for this session.")

        # Student
        try:
            student = Student.objects.get(index_number=data["index_number"], is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found or inactive.")

        # Require RFID-first (strict policy)
        if not Attendance.objects.filter(student=student, session=session).exists():
            raise serializers.ValidationError("No RFID check-in found for this student in this session.")

        data["session"] = session
        data["student"] = student
        return data

    def create(self, validated):
        session = validated["session"]
        student = validated["student"]

        att = Attendance.objects.get(student=student, session=session)
        att.is_verified = True
        att.verification_method = "QR"
        att.save()
        return att


class PermissionRequestCreateSerializer(serializers.ModelSerializer):
    # Accept student_id & session_id for writes
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student", write_only=True
    )
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassSession.objects.all(), source="session", write_only=True
    )

    class Meta:
        model = PermissionRequest
        fields = ["id", "student_id", "session_id", "reason", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated):
        # Create the permission; immediately upsert Attendance → EXCUSED
        perm = super().create(validated)

        att, _ = Attendance.objects.get_or_create(student=perm.student, session=perm.session)
        att.status = "EXCUSED"
        att.verification_method = None
        att.is_verified = True
        if not att.check_in_time:
            att.check_in_time = timezone.now()
        att.save()
        return perm


# Optional: end-of-class helper (no Enrollment yet, so minimal)
class CloseSessionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

    def validate(self, data):
        try:
            session = ClassSession.objects.get(pk=data["session_id"])
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("Session not found.")
        data["session"] = session
        return data

    def save(self, **kwargs):
        session = self.validated_data["session"]
        session.qr_active = False
        session.save()
        return session
