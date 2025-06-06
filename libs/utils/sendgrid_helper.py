import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from mailersend import emails
from config.config import settings

print(settings.MAILER_API_KEY)  # Confirm it's loading
print(settings.MAILER_FROM_EMAIL)  # Confirm it's loading


def send_email(
    to_emails: list[str],
    subject: str,
    plain_text_content: str = None,
    html_content: str = None,
):
    """
    Send an email via MailerSend.

    Args:
      to_emails:           List of recipient email addresses.
      subject:             Email subject.
      plain_text_content:  Text version of the email.
      html_content:        HTML version of the email.

    Returns:
      The response from MailerSend's API (requests.Response object).
    """
    mailer = emails.NewEmail(settings.MAILER_API_KEY)

    mail_body = {}

    mail_from = {
        "name": "Vibecast",
        "email": settings.MAILER_FROM_EMAIL,
    }

    recipients = [{"name": "User", "email": email} for email in to_emails]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)

    if html_content:
        mailer.set_html_content(html_content, mail_body)
    if plain_text_content:
        mailer.set_plaintext_content(plain_text_content, mail_body)

    # Optionally set reply-to
    mailer.set_reply_to([mail_from], mail_body)

    try:
        response = mailer.send(mail_body)
        return response
    except Exception as e:
        raise RuntimeError(f"MailerSend failed: {e}")
