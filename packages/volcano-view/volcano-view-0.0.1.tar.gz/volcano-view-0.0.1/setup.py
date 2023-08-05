from setuptools import setup

with open('version.txt') as f:
    ver = f.read().strip()

setup(
    name='volcano-view',
    version=ver,
    description='Advanced web server for Volcano',
    author='Vinogradov D',
    author_email='dgrapes@gmail.com',
    license='MIT',
    packages=['volcano.view'],
    package_data={'': ['*.json', 'www.zip']},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
