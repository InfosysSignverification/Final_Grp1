from django.db import models

class UploadedSignature(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100, choices=[('bank', 'Bank'), ('govt', 'Government Work')])
    image = models.ImageField(upload_to='signatures/')
    result = models.CharField(max_length=100)
    accuracy = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
