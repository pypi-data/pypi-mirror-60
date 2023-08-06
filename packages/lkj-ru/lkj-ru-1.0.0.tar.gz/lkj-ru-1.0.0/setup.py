from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="lkj-ru",
    version="1.0.0",
    description="A Python package to get random number between 10 to 20",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tirth-2001/lkj-ru.git",
    author="Tirth Patel",
    author_email="tirthgpatel.27@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["lkj"],
    include_package_data=True,
    install_requires=["random"],
    entry_points={
        "console_scripts": [
            "lkj-ru=lkj.fun:guess",
        ]
   
    },
)