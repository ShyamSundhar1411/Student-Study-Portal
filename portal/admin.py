from django.contrib import admin
from . models import Note,ToDo

# Register your models here.
admin.site.register(Note)
admin.site.register(ToDo)