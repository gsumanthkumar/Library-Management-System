from email import message
import imp
from .models import Transaction
from celery import shared_task
from datetime import date
from django.core.mail import send_mail
from lms import settings

@shared_task(bind=True)
def send_mail_func(self):
    today = date.today()
    due_mails = Transaction.objects.filter(due_date__lte=today,is_active=1).values_list('borrower__email',flat=True)
    for mail in due_mails:
        mail_subject = "Books Due on Date"
        message = "Hello User, You are having Books that are to be returned."
        to_email = mail
        send_mail(
            subject= mail_subject,
            message=message,
            from_email= settings.EMAIL_HOST_USER,
            recipient_list= [to_email],
            fail_silently=True,
        )
    return "Done"