from django.db import models
from users.models import Student
from courses.models import ClassSession, Course

# Create your models here.
class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("EXCUSED", "Excused"),
    ]
    METHOD_CHOICES = [
        ("RFID", "RFID"),
        ("QR", "QR"),
        ("MANUAL", "Manual"),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="attendance_records")
    check_in_time = models.DateTimeField(blank=True, null=True)
    verification_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="PRESENT")
    manual_note = models.CharField(max_length=255, blank=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_late = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("student", "session")
        indexes = [
            models.Index(fields=["session", "student"]),
            models.Index(fields=["status"]),
            models.Index(fields=["verification_method"]),
        ]
        ordering = ["session", "student"]

    def __str__(self):
        return f"{self.student.index_number} - {self.session} [{self.status}]"

class PermissionRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="permission_requests")
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="permission_requests")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "session")
        indexes = [
            models.Index(fields=["session", "student"]),
        ]
        ordering = ["session", "student"]