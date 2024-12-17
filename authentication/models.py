from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CSVFile(models.Model):
    file = models.FileField(upload_to='csv_files/')  # The directory where the files will be stored
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the file was uploaded

    def __str__(self):
        return f"CSV File uploaded at {self.uploaded_at}"
    
class Task(models.Model):
    title = models.CharField(max_length=255)  # Task title
    start_date = models.DateField()  # Start date of the task
    due_date = models.DateField()  # Due date of the task
    priority = models.CharField(max_length=50, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])  # Priority of the task
    status = models.CharField(max_length=50, choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])  # Status of the task
    assign_users = models.ManyToManyField(User, related_name='tasks')  # Users assigned to the task

    def __str__(self):
        return self.title
    
class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)

class Leader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
