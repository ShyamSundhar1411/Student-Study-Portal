from celery import shared_task
from django.core.mail import EmailMessage
from studyportal.settings import DEFAULT_FROM_EMAIL as me
from django.contrib.auth.models import User
@shared_task
def send_requested_pdf(filename,note,user_id):
    user = User.objects.get(pk=user_id)
    user_email = user.email
    subject = 'Study Portal'
    content = '''Hi {}, Hope you are doing well. We have sent the note that you generated as pdf for your comfort
Thank You
Best Regards,
Study Portal'''.format(user.username)
    email = EmailMessage(subject,content,me,[user_email])
    email.attach(filename,note,'application/pdf')
    email.send()
@shared_task
def send_requested_pdf_on_delete(filename,note,user_id):
    user = User.objects.get(pk=user_id)
    user_email = user.email
    subject = 'Study Portal'
    content = '''Hi {}, Hope you are doing well. We have sent the note that you generated as pdf for your comfort
Thank You
Best Regards,
Study Portal'''.format(user.username)
    email = EmailMessage(subject,content,me,[user_email])
    email.attach(filename,note,'application/pdf')
    email.send()