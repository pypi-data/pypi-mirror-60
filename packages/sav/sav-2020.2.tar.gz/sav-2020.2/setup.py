from setuptools import setup

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name='sav',
    version='2020.02',
    packages=['sav.info'],
    author='Sander Voerman',
    author_email='sander@savoerman.nl',
    description="Individual projects by Sander Voerman",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires='>=3.7',
    classifiers=[
        'Topic :: Documentation'
    ]
)
