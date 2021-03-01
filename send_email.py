import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from decouple import config
from tqdm import tqdm

from elimination.models import Senior

EMAIL = config('EMAIL')
EMAIL_PASSWORD = config('EMAIL_PASSWORD')


def send_winners():
    winner_list = []
    server = smtplib.SMTP_SSL('smtp.gmail.com:465')
    server.login(EMAIL, EMAIL_PASSWORD)

    for senior in Senior.objects.filter(elimination__isnull=True):
        winner_list.append(senior.first_name + " " + senior.last_name)
    for senior in Senior.objects.filter(email_subscribed=True):
        message = MIMEMultipart()
        template = Template(open('email_templates/end_game_template.txt').read())
        name = senior.first_name + " " + senior.last_name
        winners = ", ".join(str(x) for x in winner_list)
        content = template.substitute(name=name, winners=winners)
        message['From'] = EMAIL
        message['To'] = senior.email
        message['Subject'] = "Senior Elimination - That's Game! View Winners"
        message.attach(MIMEText(content, 'plain'))
        time.sleep(0.5)
        server.send_message(message)
        del message
    server.quit()


def send_game_update(game_update):
    server = smtplib.SMTP_SSL('smtp.gmail.com:465')
    server.login(EMAIL, EMAIL_PASSWORD)
    for senior in Senior.objects.filter(email_subscribed=True, is_superuser=False, elimination__isnull=True):
        message = MIMEMultipart()
        template = Template(open('email_templates/game_update_template.txt').read())
        content = template.substitute(name=senior.first_name, update_content=game_update.text)
        message['From'] = EMAIL
        message['To'] = senior.email
        message[
            'Subject'] = f'Senior Elimination - {game_update.created_at.strftime("%A %m/%d at %I:%M %p")} - Game Update!'
        message.attach(MIMEText(content, 'plain'))
        time.sleep(0.5)
        server.send_message(message)
        del message
    server.quit()


def send_reassign_targets():
    server = smtplib.SMTP_SSL('smtp.gmail.com:465')
    server.login(EMAIL, EMAIL_PASSWORD)
    for senior in tqdm(Senior.objects.filter(email_subscribed=True, senior__target__isnull=False, is_superuser=False)):
        message = MIMEMultipart()
        template = Template(open('email_templates/reassign_template.txt').read())
        target = f'{senior.target.first_name} {senior.target.last_name}'
        content = template.substitute(name=senior.first_name, target=target)
        message['From'] = EMAIL
        message['To'] = senior.email
        message['Subject'] = 'Senior Elimination - Your target has been reassigned!'
        message.attach(MIMEText(content, 'plain'))
        time.sleep(0.5)
        server.send_message(message)
        del message
    server.quit()


def send_initial_passwords():
    server = smtplib.SMTP_SSL('smtp.gmail.com:465')
    server.login(EMAIL, EMAIL_PASSWORD)
    for senior in tqdm(list(Senior.objects.filter(is_superuser=False))):
        try:
            message = MIMEMultipart()
            template = Template(open('email_templates/initial_template.txt').read())
            content = template.substitute(name=senior.first_name, student_id=senior.username,
                                          initial_password=senior.initial_password)
            message['From'] = EMAIL
            message['To'] = senior.email
            message['Subject'] = 'Senior Elimination - Initial Account Information'
            message.attach(MIMEText(content, 'plain'))
            time.sleep(0.5)
            server.send_message(message)
            del message
        except:
            print("Failed to send email to:", senior.first_name, senior.last_name)
    server.quit()
