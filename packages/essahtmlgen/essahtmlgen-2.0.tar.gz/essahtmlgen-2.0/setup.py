from setuptools import setup, find_packages

with open('README', 'r+') as desc:
    long_description = desc.read()

setup (
    name='essahtmlgen',
    version="2.0",
    packages=['essahtmlgen'],
    author='bayleaf',
    author_email='bailey.kocin@gmail.com',
    description='Create HTML files with embedded source code & images',
    long_description=long_description,
    package_data={'essahtmlgen': ['data/*.jpg']},
    include_package_data=True,
    entry_points = {
        'console_scripts' : [
            'essahtmlgen = essahtmlgen.essahtmlgen:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

