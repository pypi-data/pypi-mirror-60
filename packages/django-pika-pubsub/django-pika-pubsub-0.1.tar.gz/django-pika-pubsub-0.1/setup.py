import os

from setuptools import setup

CLASSIFIERS = [
    'Framework :: Django',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Framework :: Django :: 3.0',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development',
]

install_requires = [
    'pika',
]


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()


setup(
    name="django-pika-pubsub",
    description="A Django app to publish and consume rmq-messages via Pika.",
    author="Bogdanov Dmitry",
    readme=readme,
    author_email="bogdanov@phie.ru",
    install_requires=install_requires,
    python_requires=">=3.5",
    classifiers=CLASSIFIERS,
    zip_safe=False,
)
