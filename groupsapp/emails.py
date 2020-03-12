from django.core.mail import send_mail

frommail = 'noreply@groupmanager.co.uk'
def welcome(name,email):
    send_mail(
        'Welcome to GroupManager',
        'Hi '+name+', Welcome to GroupManager.',
        frommail,
        [email]
    )