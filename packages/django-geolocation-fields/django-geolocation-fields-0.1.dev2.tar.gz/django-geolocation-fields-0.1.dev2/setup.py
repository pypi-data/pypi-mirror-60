import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-geolocation-fields", # Replace with your own username
    version="0.1.dev2",
    author="GOUNTENI DAMBE TCHIMBIANDJA",
    author_email="dambemondo@gmail.com",
    description="A Django app to work with geolocation fields without a spatial database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/syk1k/django-geolocation-fields",
    packages=setuptools.find_packages(),
    install_requires=[
        'Django>=2.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)