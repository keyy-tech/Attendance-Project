from rest_framework import viewsets, permissions
from .models import Student, Lecturer
from .serializers import StudentSerializer, LecturerSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by("index_number")
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all().order_by("staff_id")
    serializer_class = LecturerSerializer
    permission_classes = [permissions.AllowAny]
