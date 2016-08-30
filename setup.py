from setuptools import setup


setup(
    name='django-email-multi-related',
    install_requires={
        'beautifulsoup4>=4.4.1',
        'pynliner>=0.5.2',
    },
    setup_requires={
        'beautifulsoup4>=4.4.1',
        'pynliner>=0.5.2',
    },
    packages=[
        'django_email_multi_related',
        'django_email_multi_related.templatetags',
    ],
    version='0.1.8',
    platforms=['all'],
    license='BSD',
    description='',
)
