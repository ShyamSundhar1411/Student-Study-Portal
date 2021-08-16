from django.contrib import admin
from . models import Note,HomeWork,ToDo

# Register your models here.
admin.site.register(Note)
admin.site.register(HomeWork)
admin.site.register(ToDo)