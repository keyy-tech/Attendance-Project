from django.db import models

# Create your models here.
class Student(models.Model):
    index_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    # Add other fields as needed

    def __str__(self):
        return f"{self.index_number} - {self.first_name} {self.last_name}"
