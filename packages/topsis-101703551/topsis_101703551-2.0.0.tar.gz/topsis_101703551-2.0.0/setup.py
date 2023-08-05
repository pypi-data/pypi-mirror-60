from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_101703551",
    version="2.0.0",
    description="A Python package to rank ML models/choices using topsis technique",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sirishbhu/topsis",
    author="Sirish Bhudolia",
    author_email="sirishbhudolia88@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101703551"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "topsis-package-1=topsis_101703551.__init__:main",
        ]
    },
)
