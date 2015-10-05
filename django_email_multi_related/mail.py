# -*- coding: utf-8 -*-

from __future__ import absolute_import

import copy
import hashlib
import os
from email.mime.base import MIMEBase

import pynliner
from bs4 import BeautifulSoup
from bs4.element import Comment
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart
from django.template.loader import render_to_string


class EmailMultiRelatedCore(EmailMultiAlternatives):
    related_subtype = 'related'

    def __init__(self, *args, **kwargs):
        self.related_attachments = []
        self.related_attachments_filename_content_id = []
        super(EmailMultiRelatedCore, self).__init__(*args, **kwargs)

    def attach_related(self, filename=None, content=None, mimetype=None, filename_content_id=None):
        if filename_content_id is None:
            m = hashlib.md5()
            m.update(filename)
            filename_content_id = m.hexdigest()
        if filename_content_id not in self.related_attachments_filename_content_id:
            if isinstance(filename, MIMEBase):
                assert content == mimetype == None
                self.related_attachments.append(filename)
            else:
                assert content is not None
                self.related_attachments.append((filename, content, mimetype, filename_content_id))
            self.related_attachments_filename_content_id.append(filename_content_id)
        return filename_content_id

    def attach_related_file(self, path, mimetype=None):
        filename = os.path.basename(path)
        content = open(path, 'rb').read()
        return self.attach_related(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(self._create_related_attachments(self._create_alternatives(msg)))

    def _create_related_attachments(self, msg):
        encoding = self.encoding or 'utf-8'
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for related in self.related_attachments:
                msg.attach(self._create_related_attachment(*related))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None, filename_content_id=None):
        attachment = super(EmailMultiRelatedCore, self)._create_attachment(filename, content, mimetype)
        if filename:
            mimetype = attachment['Content-Type']
            del(attachment['Content-Type'])
            del(attachment['Content-Disposition'])
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-Type', mimetype, name=filename)
            attachment.add_header('Content-ID', '<%s>' % filename_content_id)
        return attachment


class EmailMultiRelated(EmailMultiRelatedCore):
    alternative_subtype = 'related'

    def __init__(self, subject, to, template, context):
        super(EmailMultiRelated, self).__init__(subject=subject, to=to)

        self.template = template
        self.context = context

        self.body = self._render_text()
        self.attach_alternative(self._render_html(), 'text/html')

    def _render_html(self):
        context = copy.copy(self.context)
        context['email_image_inline_object'] = self

        html = render_to_string(self._get_template('html'), context)

        html = self._inline_css(html)
        html = self._clear_html(html)

        return html

    def _render_text(self):
        return render_to_string(self._get_template('txt'), self.context)

    def _inline_css(self, html):
        with open(self._get_template_file('css')) as f:
            css = f.read()

        inliner = pynliner.Pynliner().from_string(html)
        inliner = inliner.with_cssString(css)
        return inliner.run()

    def _clear_html(self, content):
        html = BeautifulSoup(content, 'lxml')

        # remove comments
        for item in html.find_all(text=lambda t: isinstance(t, Comment)):
            item.extract()

        # remove classes and ids
        for item in html.find_all():
            if 'class' in item.attrs:
                del item.attrs['class']

            if 'id' in item.attrs:
                del item.attrs['id']

        return unicode(html)

    def _get_template_file(self, file_type):
        return os.path.join(
            settings.EMAIL_TEMPLATES,
            self.template,
            '{}.{}'.format(self.template, file_type))

    def _get_template(self, file_type):
        return os.path.join(
            'emails',
            self.template,
            '{}.{}'.format(self.template, file_type))
