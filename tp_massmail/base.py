# encoding: utf-8

from email.header import Header
from email.utils import formataddr

from emails.django import Message
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import get_template
from django.utils import translation
from django.conf import settings
from post_office import mail

from tp_massmail.util import get_host_url, get_prefix_and_site


class NotificationEmail(object):
    subject_template = None
    text_body_template = None
    html_body_template = None

    def send(self, to_email, to_name=None, request=None, **context):
        m = Message(subject=get_template(self.subject_template),
                    text=self.text_body_template and get_template(self.text_body_template) or None,
                    html=self.html_body_template and get_template(self.html_body_template) or None,
                    mail_from=settings.EMAIL_NOTIFICATIONS_FROM,
                    mail_to=(to_name, to_email))
        context.setdefault('host_url', get_host_url(request))  # Во всех письмах нужны абсолютные адреса.
        m.send(context={'context': context, 'request': request})


class MassSendEmails(object):
    '''
    Базовый класс для массовых рассылок
    '''
    template_subject = None
    template_text = None
    template_html = None
    extra_headers = None
    BULK_SIZE = getattr(settings, 'EMAIL_BULK_SIZE', 10000)

    def __init__(self, *args, **kwargs):
        self.emails = self.get_emails()
        self.defaults = get_prefix_and_site()

    def get_mail_from(self):
        email = settings.EMAIL_NOTIFICATIONS_FROM
        if isinstance(email, str):
            return email
        elif isinstance(email, list) or isinstance(email, tuple):
            assert len(email) == 2, 'Email should be tuple of size 2 (name, email)'
            return formataddr((str(Header(email[0], 'utf-8')), email[1]))
        else:
            raise Exception('Email must be sting or tuple (name, email)')

    def get_subject(self, email=None):
        if self.template_subject:
            return get_template(self.template_subject).render(self.get_context(email)).strip().replace('\n', ' ')
        return ''

    def get_text(self, email=None):
        if self.template_text:
            return get_template(self.template_text).render(self.get_context(email))
        return None

    def get_html(self, email=None):
        if self.template_html:
            return get_template(self.template_html).render(self.get_context(email))

    def send(self):
        for msgs in self.generate_messages():
            mail.send_many(msgs)

    def generate_messages(self):
        msgs = []
        for e in self.emails:
            try:
                validate_email(e)
            except ValidationError:
                continue
            tmp = {
                'sender': self.get_mail_from(),
                'recipients': [e],
            }
            translation.activate(settings.LANGUAGE_CODE)
            subject, message, html_message = self.get_subject(e), self.get_text(e), self.get_html(e)
            translation.deactivate()
            if subject:
                tmp['subject'] = subject
            if message:
                tmp['message'] = message
            if html_message:
                tmp['html_message'] = html_message
            extra_headers = self.get_extra_headers(e)
            if extra_headers:
                tmp['headers'] = extra_headers
            msgs.append(tmp)
            if len(msgs) == self.BULK_SIZE:
                yield msgs
                msgs = []
        if msgs:
            yield msgs

    def get_extra_headers(self, email=None):
        return self.extra_headers

    def get_site(self):
        return '{prefix}://{site}'.format(**self.defaults)

    def get_emails(self):
        raise NotImplementedError

    def get_context(self, email=None):
        raise NotImplementedError
