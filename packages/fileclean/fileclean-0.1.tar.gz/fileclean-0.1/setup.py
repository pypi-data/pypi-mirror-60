from setuptools import setup, find_packages

setup(
    name="fileclean",
    version="0.1",
    author="Brendon Lin",
    author_email="brendon.lin@outlook.com",
    description="Package for clean local files",
    packages=find_packages(),
    install_requires=["loguru>=0.4.1"],
    entry_points={"console_scripts": ["fileclean = fileclean.view:main"]},
)
