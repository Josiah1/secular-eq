from setuptools import setup, find_packages

setup(
    name="secular-equilibrium",
    version="1.0.0",
    author="Jinjing Li",
    description="Secular equilibrium calculator for radioactive decay chains",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Josiah1/secular-eq",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "radioactivedecay>=0.6.0",
    ],
    entry_points={
        "console_scripts": [
            "secular-eq=secular_equilibrium.cli:main",
        ],
    },
)
