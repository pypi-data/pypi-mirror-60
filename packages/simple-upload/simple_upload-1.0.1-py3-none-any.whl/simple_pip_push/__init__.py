#!/usr/bin/env python

# Apparently I can't set up a console entry point for the file itself, so I have to make a funtion.


def main():
    import os
    SETUP_PY_DEFAULT = '''import setuptools
    with open("README.md", "r") as fh:
        long_description = fh.read()
    setuptools.setup(
        name='pip-package-name-here',
        version='0.0.0',
        author="Your name",
        author_email="your_email@example.com",
        description="A short description",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://example.com",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    '''
    if os.path.exists('./setup.py'):
        os.system('python setup.py sdist bdist_wheel')
        os.system('python -m twine upload dist/*')
        answer = input('Do you want to make a Git commit? (y/n) ')
        if 'y' in answer.lower():
            os.system('git add -A')
            os.system('git commit')
        raise SystemExit(0)
    else:
        answer = input('There is no setup.py. Do you want to make one? (y/n) ')
        if 'y' in answer.lower():
            try:
                file = open('setup.py', 'w')
                file.write(SETUP_PY_DEFAULT)
                file.close()
                print('Success. Now edit it.')
            except:
                print('Failed')
        raise SystemExit(1)


main()  # Run the main function if run from CLI directly
