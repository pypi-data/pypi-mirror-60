import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="analytics_insights",
    version="0.0.1",
    author="Alvaro Brandon",
    author_email="alvaro.brandon@kapsch.net",
    description="A library to produce insights about both Analytics Data and Analytics Deployments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gde.kapschtraffic.com/brandon/analytics_insights",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)