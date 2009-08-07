from django.db import models

# Create your models here.
class Friend(models.Model):
	location = models.CharField(max_length=20)
	post_date = models.DateTimeField('post date')
