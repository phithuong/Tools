from django.db import models
from django import forms
from datetime import datetime
from .constants import GENDER_CHOICES


class User(models.Model):
    """
    Class define user information
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True, null=False)
    user_code = models.CharField(unique=True, max_length=30, null=False)
    user_name = models.CharField(unique=True, max_length=100, null=False)
    full_name = models.CharField(unique=True, max_length=100, null=False)
    password = models.BinaryField(max_length=256, editable=True, null=True)
    fb_link = models.URLField(unique=True, null=True)
    email = models.EmailField(unique=True, null=True)
    address = models.CharField(max_length=256, null=True)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    salt = models.BinaryField(max_length=256, null=True)
    is_valid = models.BooleanField(null=False)

    class Meta:
        db_table = 'User'

    def publish(self):
        self.create_date = datetime.now()
        self.update_date = self.create_date
        self.is_valid = True
        self.save()

    def update(self, **kwargs):
        self.update_date = datetime.now()
        self.save()
