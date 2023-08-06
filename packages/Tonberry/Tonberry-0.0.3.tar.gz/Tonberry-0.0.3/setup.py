from setuptools import setup, find_packages

from tonberry import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name="Tonberry",
    version=__version__,
    description="ASGI compliant web microframework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anthony Post",
    author_email="postanthony3000@gmail.com",
    license="MIT License",
    url="https://github.com/Ayehavgunne/Tonberry/",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": ["mypy", "black", "isort"]},
    python_requires=">=3.7",
)
