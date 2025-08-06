from django.db import models

# Create your models here.
class Student(models.Model):
    index_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Hardware identification fields
    rfid_tag = models.CharField(max_length=50, unique=True, blank=True, null=True)
    fingerprint_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Academic info
    program = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['index_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.index_number} - {self.first_name} {self.last_name}"
    



class Lecturer(models.Model):
    staff_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Academic info
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=50, blank=True)  # Dr., Prof., Mr., Ms., etc.
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['staff_id']
        verbose_name = 'Lecturer'
        verbose_name_plural = 'Lecturers'

    def __str__(self):
        title_prefix = f"{self.title} " if self.title else ""
        return f"{self.staff_id} - {title_prefix}{self.first_name} {self.last_name}"
    

