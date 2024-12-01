from django.db import models

# Create your models here.
class CSVFile(models.Model):
    file = models.FileField(upload_to='csv_files/')  # The directory where the files will be stored
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the file was uploaded

    def __str__(self):
        return f"CSV File uploaded at {self.uploaded_at}"