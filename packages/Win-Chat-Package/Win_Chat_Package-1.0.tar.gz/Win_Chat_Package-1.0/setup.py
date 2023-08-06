from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='Win_Chat_Package',
    version='1.0',
    packages=['Testchatpkg'],
    url='https://github.com/riturajpandey/Win_Chat_Package',
    license='',
    author='Ashwini Bokade',
    author_email='ashwini_bokade@yahoo.com',
    description='Testing package publish',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ]
)
