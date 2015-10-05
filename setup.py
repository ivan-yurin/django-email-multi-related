from setuptools import setup
from django_email_multi_related import __version__


setup(
    name='django-email-multi-related',
    install_requires={
        'beautifulsoup4>=4.4.1',
        'pynliner>=0.5.2',
    },
    packages=[
        'django_email_multi_related',
        'django_email_multi_related.templatetags',
    ],
    version=__version__,
    platforms=['all'],
    license='BSD',
    description='',
    long_description=open('README.md').read(),
)
