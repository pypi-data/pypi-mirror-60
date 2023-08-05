import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='simple-upload',
    entry_points={
        'console_scripts': ['pip-upload=simple_pip_push:main'],
    },
    version='1.0.2',
    author="Bruce Blore",
    author_email="bruceblore@protonmail.com",
    description="A script to re-build and upload your package without having to remember the exact commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/0100001001000010/simple-upload",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
