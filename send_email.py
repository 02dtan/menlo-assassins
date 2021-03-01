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


def send_initial_passwords():
    initial_passwords = {line.split(",")[0]: line.split(",")[1] for line in
                         open("initial_passwords.csv", "r").readlines()}

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL, EMAIL_PASSWORD)
    seniors = tqdm(list(Senior.objects.filter(is_superuser=False)))
    for senior in seniors:
        try:
            message = MIMEMultipart()
            template = Template(open('email_templates/initial_template.txt').read())
            content = template.substitute(name=senior.first_name, student_id=senior.username,
                                          initial_password=initial_passwords[senior.username])
            message['From'] = EMAIL
            message['To'] = senior.email
            message['Subject'] = 'Senior Elimination - Initial Account Information'
            message.attach(MIMEText(content))
            seniors.set_description(f"Sending email to {senior.username}: {senior.first_name} {senior.last_name}")
            server.send_message(message)
            time.sleep(8)
            del message
        except Exception as e:
            print(e)
            print("Failed to send email to:", senior.username)
    server.quit()
