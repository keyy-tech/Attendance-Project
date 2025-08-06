from rest_framework import serializers
from .models import Student, Lecturer

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id", "index_number", "first_name", "last_name", "email",
            "phone_number", "rfid_tag", "program", "year_of_study", "is_active"
        ]


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = [
            "id", "staff_id", "first_name", "last_name", "email",
            "phone_number", "department", "title", "is_active"
        ]
