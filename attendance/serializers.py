from rest_framework import serializers
from users.models import Student
from courses.models import ClassSession
from .models import Attendance, Device

class RFIDCheckInSerializer(serializers.Serializer):
    rfid_tag = serializers.CharField(required=False, allow_blank=True)
    index_number = serializers.CharField(required=False, allow_blank=True)
    session_id = serializers.IntegerField(required=True)
    device_id = serializers.IntegerField(required=False)

    def validate(self, data):
        rfid_tag = data.get("rfid_tag")
        index_number = data.get("index_number")
        session_id = data.get("session_id")

        if not rfid_tag and not index_number:
            raise serializers.ValidationError("Provide either rfid_tag or index_number.")

        # Student
        try:
            if rfid_tag:
                student = Student.objects.get(rfid_tag=rfid_tag, is_active=True)
            else:
                student = Student.objects.get(index_number=index_number, is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found or inactive.")

        # Session
        try:
            session = ClassSession.objects.get(pk=session_id)
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("ClassSession not found.")

        # Optional device
        device = None
        device_id = data.get("device_id")
        if device_id:
            try:
                device = Device.objects.get(pk=device_id)
            except Device.DoesNotExist:
                raise serializers.ValidationError("Device not found.")

        data["student"] = student
        data["session"] = session
        data["device"] = device
        return data


class AttendanceSerializer(serializers.ModelSerializer):
    student_index = serializers.CharField(source="student.index_number", read_only=True)
    course_code = serializers.CharField(source="session.course.code", read_only=True)
    session_datetime = serializers.DateTimeField(source="session.session_date", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "student_index",
            "course_code",
            "session_datetime",
            "status",
            "verification_method",
            "check_in_time",
            "is_late",
            "manual_note",
            "marks_awarded",
        ]
