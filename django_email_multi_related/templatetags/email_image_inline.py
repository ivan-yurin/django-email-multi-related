# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.template import Library
from django.contrib.staticfiles.storage import staticfiles_storage

from django_email_multi_related.mail import EmailMultiRelated


register = Library()


@register.simple_tag(takes_context=True)
def email_embedded_static(context, path):
    email = context.get('email_image_inline_object')
    expanded_path = os.path.join(settings.EMAIL_TEMPLATES, email.template, path)

    if isinstance(email, EmailMultiRelated):
        return 'cid:' + email.attach_related_file(expanded_path)

    return staticfiles_storage.url(path)
