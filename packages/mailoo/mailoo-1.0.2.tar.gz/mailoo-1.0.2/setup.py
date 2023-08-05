import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="mailoo", # Nome do Pacote
    version="1.0.2",
    author="Wellington Gadelha",
    author_email="contato.informeai@gmail.com",
    description="Pacote para criaçao/envio de Emails, via SMTP protocolo.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/informeai/mailoo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)