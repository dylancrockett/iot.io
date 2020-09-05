from setuptools import setup
import iotio

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="iot.io",
    version=iotio.__version__,
    packages=["iotio"],
    author="Dylan Crockett",
    author_email="dylanrcrockett@gmail.com",
    license="MIT",
    description="A management API for connecting and managing Clients via websocket connections.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dylancrockett/iot.io",
    project_urls={
        "Documentation": "https://iotio.readthedocs.io/",
        "Source Code": "https://github.com/dylancrockett/iot.io"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'gevent',
        'gevent-websocket',
        'flask',
        'flask-sockets',
    ],
    python_requires='>=3.7'
)
