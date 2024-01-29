import pathlib
from setuptools import setup, find_packages

VERSION = "0.0.6"

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [
        requirement
        for requirement in fh.read().splitlines()
        if not requirement.startswith("#")
    ]

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="ragcore",
    version=VERSION,
    description="A library to build Retrieval Augmentation Applications with only a few lines of code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daved01/ragcore",
    author="David Kirchhoff",
    author_email="david.kirchhoff@mail.utoronto.ca",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="retrieval augmented generation, rag, development, artificial intelligence, large language models",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ragcore = ragcore.cli:entrypoint",
        ]
    },
    packages=find_packages(include=["ragcore*"], exclude=["tests"]),
    # package_dir={"": "ragcore"},
    include_package_data=True,
    package_data={
        "ragcore": ["configuration.yaml", "requirements.txt"],
    },
    python_requires=">=3.10, <4",
    project_urls={
        "Bug Reports": "https://github.com/daved01/ragcore/issues",
        "Funding": "https://github.com/sponsors/daved01",
        "Say Thanks!": "https://www.paypal.com/donate/?hosted_button_id=23YUGLRRTNDMS",
        "Source": "https://github.com/daved01/ragcore",
        "Documentation": "https://daved01.github.io/ragcore/",
    },
)
