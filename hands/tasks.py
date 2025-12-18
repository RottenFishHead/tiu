from thisisus import settings
from django.contrib.auth import get_user_model
from thisisus.celery import app
from django.core.mail import send_mail
import json
from celery import shared_task

# app = Celery('thisisus', broker='redis://red-cmguf5nqd2ns73fmpd6g:6379')

# #This must be here for redis to work on heroku
# app.conf.update(BROKER_URL=settings.REDIS_URL,
#             CELERY_RESULT_BACKEND=settings.REDIS_URL)
@shared_task
def send_email_task(serialized_details, email_body):
    
    # Deserialize the hand_details
    hand_dict = json.loads(serialized_details)
    recipient_email = hand_dict.get('kjsonnenberg@me.com')
    subject = 'New Hand'

    # Send email using Django's send_mail function
    send_mail(
        subject,
        email_body,
        'kjsonnenberg@gmail.com',
        [recipient_email],
        fail_silently=False,
        auth_user='kjsonnenberg@gmail.com',  # Sender's Gmail email
        auth_password='frat gubn kxwu bxvm',
    )

@shared_task(bind=True)
def send_mail_func(self):
    #operations
    users = get_user_model().objects.all()
    for user in users:
        mail_subject="Hye from celery"
        message="Yaaaa....I have completed this task by celery!!"
        to_email=user.email
        send_mail(
            subject= mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=True,
        )
    return "Done"