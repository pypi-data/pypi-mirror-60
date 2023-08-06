import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-oracle-utils", # Replace with your own username
    version="0.0.1",
    author="Robbie Meyers",
    author_email="robbie.meyers@gmail.com",
    description="Adds support for additional Oracle functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmeyers4/django-oracle-utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)