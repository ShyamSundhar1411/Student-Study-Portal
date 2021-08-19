import uuid
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from tinymce.models import HTMLField
from autoslug import AutoSlugField

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length = 200)
    subject = models.CharField(max_length = 200)
    updated_on = models.DateField(auto_now = True)
    important = models.BooleanField(default = False)
    notes = HTMLField()
    slug = AutoSlugField(populate_from = "title",unique = True,blank = True,editable = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.title

class ToDo(models.Model):
    title = models.CharField(max_length = 200)
    memo = models.TextField(max_length = 200)
    created = models.DateTimeField(auto_now_add = True)
    important = models.BooleanField(default = False)
    is_completed = models.BooleanField(default = False)
    slug = AutoSlugField(populate_from = "title",unique = True,blank = True,editable = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.title
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    avatar = models.ImageField(upload_to = "avatar/",blank = True)
    slug = models.SlugField(blank = True,unique = True)
    def __str__(self):
        return self.user.username
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = uuid.uuid4()
        super(Profile,self).save(*args,**kwargs)
@receiver(post_save,sender = User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user = instance)
        instance.profile.save()
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()