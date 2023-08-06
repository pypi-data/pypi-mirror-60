import setuptools

CLIENT_VERSION = "2.1.1"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rename-beep-files",
    version=CLIENT_VERSION,
    scripts=['rename-beep-files'],
    author="Mattia Sanchioni",
    author_email="mattia.sanchioni.dev@gmail.com",
    description="Rename Beep files",
    keywords="rename files beep Beep",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mett96/rename-beep-files",
    packages=setuptools.find_packages(),
    license="GPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
