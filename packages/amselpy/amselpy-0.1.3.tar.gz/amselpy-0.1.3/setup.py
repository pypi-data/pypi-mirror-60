import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amselpy", # Replace with your own username
    version="0.1.3",
    author="Moritz Gut",
    author_email="hello@moritzgut.de",
    description="Take control of you Amsel bot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baumeise/amselpy.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)