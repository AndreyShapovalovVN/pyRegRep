from setuptools import setup, find_packages

setup(
    name="pyRegRep",
    version="11",
    description="Бібліотека для роботи з реєстрами та репозитаріями в Україні",
    packages=find_packages(),
    license="MIT",
    author="Andrii Shapovalov",
    author_email="mt.andrey@gmail.com",
    include_package_data=True,
    install_requires=[
        "lxml>=5.2.1",
        "xmltodict>=0.13.0",
    ],
)
