from django.db import models

# Create your models here.

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)


    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    session_date = models.DateTimeField()
    location = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.course.code} @ {self.session_date:%Y-%m-%d %H:%M}"
