# -*- coding: utf-8 -*-

from __future__ import absolute_import

import copy
import hashlib
import os
from email.mime.image import MIMEImage

import pynliner
from bs4 import BeautifulSoup
from bs4.element import Comment
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailMultiRelatedCore(EmailMultiAlternatives):
    def attach_related_file(self, path):
        filename = os.path.basename(path)
        content_id = hashlib.md5(filename).hexdigest()

        content = open(path, 'rb').read()

        mime = MIMEImage(content)

        mime_type = mime['Content-Type']

        del mime['Content-Type']
        del mime['Content-Disposition']

        mime.add_header('Content-ID', '<{}>'.format(content_id))
        mime.add_header('Content-Disposition', 'inline', filename=filename)
        mime.add_header('Content-Type', mime_type, name=filename)

        self.attach(mime)

        return content_id


class EmailMultiRelated(EmailMultiRelatedCore):
    def __init__(self, subject, to, template, context):
        self.template = template
        self.context = context

        super(EmailMultiRelated, self).__init__(subject=subject, to=to)
        self.mixed_subtype = 'related'

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
