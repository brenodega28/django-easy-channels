import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-easy-channels",  # Replace with your own username
    version="0.0.1",
    author="Breno Gomes",
    author_email="brenodega28@gmail.com",
    description="Lightweight framework for quickly making socket consumers using Django and DjangoChannels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brenodega28/django_easy_channels",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
