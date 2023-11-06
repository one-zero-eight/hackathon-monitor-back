__all__ = ["SMTPRepository"]

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_validator import validate_email, EmailNotValidError
from jinja2 import Template

from src.config import settings
from src.modules.smtp.abc import AbstractSMTPRepository
from src.modules.alerts.schemas import MappedAlert


class SMTPRepository(AbstractSMTPRepository):
    def __init__(self):
        self._server = smtplib.SMTP(settings.SMTP.SERVER, settings.SMTP.PORT)

    def send(self, message: str, to: str):
        try:
            valid = validate_email(to)
            to = valid.normalized
        except EmailNotValidError as e:
            raise ValueError(e)
        self._server.starttls()
        self._server.login(settings.SMTP.USERNAME, settings.SMTP.PASSWORD.get_secret_value())
        self._server.sendmail(settings.SMTP.USERNAME, to, message)
        self._server.quit()

    def send_connect_email(self, email: str, auth_code: str):
        mail = MIMEMultipart("related")
        # Jinja2 for html template
        main = Template(
            """
            <html>
                <body>
                    <p>Hi!</p>
                    <p>Here is your temporary code for registration: {{ code }}</p>
                </body>
            </html>
            """,
            autoescape=True,
        )

        html = main.render(code=auth_code)
        msgHtml = MIMEText(html, "html")
        mail.attach(msgHtml)

        mail["Subject"] = "Registration in Monitoring Service"
        mail["From"] = settings.SMTP.USERNAME
        mail["To"] = email

        self._server.starttls()
        self._server.login(settings.SMTP.USERNAME, settings.SMTP.PASSWORD.get_secret_value())
        self._server.sendmail(settings.SMTP.USERNAME, email, mail.as_string())
        self._server.quit()

    def send_alert_message(
        self,
        email: str,
        mapped_alert: "MappedAlert",
    ):
        mail = MIMEMultipart("related")
        # Jinja2 for html template
        main = Template(
            """
            {% if alert.status == "resolved" %}
            Проблема устранена: <b>{{ alert.title }}</b> ✅ <br/>
            {% else %}
            {% set emoji = "⚠️" if alert.severity == "warning" else "🚨" %}
            {{ emoji }} <b>{{ alert.title }}</b> {{ emoji }} <br/>
            {% endif %}

            Сервер: <b>{{ alert.target_alias }} </b> <br/>

            Время: {{ alert.timestamp.strftime("%Y-%m-%d %H:%M:%S") }} <br/>

            {% if alert.description %}
            Описание: <br/>
            {{ alert.description }} <br/>
            {% endif %}
            """,
            autoescape=True,
        )

        html = main.render(alert=mapped_alert)
        msgHtml = MIMEText(html, "html")
        mail.attach(msgHtml)
        subject = f"Оповещение: {mapped_alert.target_alias} {mapped_alert.title}"
        mail["Subject"] = subject
        mail["From"] = settings.SMTP.USERNAME
        mail["To"] = email

        self._server.starttls()
        self._server.login(settings.SMTP.USERNAME, settings.SMTP.PASSWORD.get_secret_value())
        self._server.sendmail(settings.SMTP.USERNAME, email, mail.as_string())
        self._server.quit()

    def close(self):
        self._server.quit()
