from django import forms
from . models import Profile
from django.contrib.auth.models import User

class SearchForm(forms.Form):
    search = forms.CharField(label = 'Search')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']