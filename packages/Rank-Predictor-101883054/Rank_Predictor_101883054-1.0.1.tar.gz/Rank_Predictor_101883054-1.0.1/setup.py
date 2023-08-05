

from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Rank_Predictor_101883054",
    version="1.0.1",
    description="A python package to predict the rank of a MCDMP using topsis",
    long_description=readme(),
    long_description_content_type="text/markdown",
    #url="https://github.com/nikhilkumarsingh/weather-reporter",
    author="Mehak Garg",
    #author_email="nikhilksingh97@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["top"],
    include_package_data=True,
    install_requires=["pandas","numpy"],
    entry_points={
        "console_scripts": [
            "Rank_Predictor_101883054=top.topsis:main",
        ]
    },
)