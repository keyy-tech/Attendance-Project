from django.db import models


class Student(models.Model):
    index_number = models.CharField(max_length=20, unique=True)
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # RFID is the primary student check-in method
    rfid_tag = models.CharField(max_length=50, unique=True, blank=True, null=True)

    program       = models.CharField(max_length=120, blank=True)
    year_of_study = models.PositiveIntegerField(blank=True, null=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["index_number"]

    def __str__(self):
        return f"{self.index_number} - {self.first_name} {self.last_name}"


class Lecturer(models.Model):
    staff_id     = models.CharField(max_length=20, unique=True)
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)

    department = models.CharField(max_length=120, blank=True)
    title      = models.CharField(max_length=50, blank=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["staff_id"]

    def __str__(self):
        prefix = f"{self.title} " if self.title else ""
        return f"{self.staff_id} - {prefix}{self.first_name} {self.last_name}"
