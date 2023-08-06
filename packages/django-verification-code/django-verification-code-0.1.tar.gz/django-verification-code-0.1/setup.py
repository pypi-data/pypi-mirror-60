import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-verification-code',
    version='0.1',
    packages=['codigo'],
    description='Phone verification with twilio',
    long_description=README,
    author='Rafael Cardenas',
    author_email='rcardenas@softicsolutions.mx',
    url='https://git-codecommit.us-east-2.amazonaws.com/v1/repos/django-verification-code',
    license='MIT',
    install_requires=[
        'Django>2',
        'djangorestframework==3.11.0',
        'twilio==6.35.2'
    ]
)