from rest_framework import serializers
from .models import Course, ClassSession


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "code", "name"]


class ClassSessionSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "course",
            "course_code",
            "course_name",
            "session_date",
            "location",
        ]
