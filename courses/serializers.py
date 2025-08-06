from rest_framework import serializers
from .models import Course, TimeTable, ClassSession
from users.models import Lecturer
from users.serializers import LecturerSerializer


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "code", "name"]


class TimeTableSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    lecturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecturer.objects.all(), source="lecturer", write_only=True
    )
    course = CourseSerializer(read_only=True)
    lecturer = LecturerSerializer(read_only=True)

    class Meta:
        model = TimeTable
        fields = [
            "id", "course", "course_id", "lecturer", "lecturer_id",
            "day_of_week", "start_time", "duration_minutes", "location"
        ]


class ClassSessionSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    lecturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecturer.objects.all(), source="lecturer", write_only=True
    )
    course = CourseSerializer(read_only=True)
    lecturer = LecturerSerializer(read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            "id", "course", "course_id", "timetable", "lecturer", "lecturer_id",
            "session_date", "start_time", "duration_minutes", "location",
            "is_adhoc", "require_qr_verification", "qr_active",
            "session_qr_token", "is_cancelled", "created_at"
        ]
        read_only_fields = ["session_qr_token", "created_at"]


# --------- Special / Workflow serializers for Courses ---------

class CreateAdhocSessionSerializer(serializers.Serializer):
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source="course")
    lecturer_id = serializers.PrimaryKeyRelatedField(queryset=Lecturer.objects.all(), source="lecturer")
    session_date = serializers.DateField()
    start_time = serializers.TimeField()
    duration_minutes = serializers.IntegerField(min_value=15, max_value=300)
    location = serializers.CharField(allow_blank=True, required=False)
    require_qr_verification = serializers.BooleanField(default=False)

    def validate(self, data):
        from .models import ClassSession
        exists = ClassSession.objects.filter(
            course=data["course"], lecturer=data["lecturer"],
            session_date=data["session_date"], start_time=data["start_time"]
        ).exists()
        if exists:
            raise serializers.ValidationError(
                "A session already exists for this course/lecturer at that date/time."
            )
        return data

    def create(self, validated):
        from .models import ClassSession
        return ClassSession.objects.create(
            course=validated["course"],
            lecturer=validated["lecturer"],
            session_date=validated["session_date"],
            start_time=validated["start_time"],
            duration_minutes=validated["duration_minutes"],
            location=validated.get("location", ""),
            is_adhoc=True,
            require_qr_verification=validated["require_qr_verification"],
        )


class SessionQRActivateSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

    def validate(self, data):
        from .models import ClassSession
        try:
            session = ClassSession.objects.get(pk=data["session_id"], is_cancelled=False)
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("Session not found or cancelled.")
        session.ensure_session_qr_token()
        data["session"] = session
        return data

    def save(self, **kwargs):
        session = self.validated_data["session"]
        session.qr_active = True
        session.require_qr_verification = True
        session.save()
        return session


class SessionQRDeactivateSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

    def validate(self, data):
        from .models import ClassSession
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


class SessionCancelSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

    def validate(self, data):
        from .models import ClassSession
        try:
            session = ClassSession.objects.get(pk=data["session_id"])
        except ClassSession.DoesNotExist:
            raise serializers.ValidationError("Session not found.")
        data["session"] = session
        return data

    def save(self, **kwargs):
        session = self.validated_data["session"]
        session.is_cancelled = True
        session.save()
        return session
