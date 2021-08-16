from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from autoslug import AutoSlugField

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length = 200)
    updated_on = models.DateField(auto_now = True)
    notes = HTMLField()
    slug = AutoSlugField(populate_from = "title",unique = True,blank = True,editable = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.title

class HomeWork(models.Model):
    title = models.CharField(max_length = 200)
    subject = models.CharField(max_length = 200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    due = models.DateTimeField(null = True,blank = True)
    is_completed = models.BooleanField(default = False)
    important = models.BooleanField(default = False)
    slug = AutoSlugField(populate_from = "title",unique = True,blank = True,editable = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.title

class ToDo(models.Model):
    title = models.CharField(max_length = 200)
    memo = models.TextField(max_length = 200)
    created = models.DateTimeField(auto_now_add = True)
    datecompleted = models.DateTimeField(null = True,blank = True)
    important = models.BooleanField(default = False)
    slug = AutoSlugField(populate_from = "title",unique = True,blank = True,editable = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.title