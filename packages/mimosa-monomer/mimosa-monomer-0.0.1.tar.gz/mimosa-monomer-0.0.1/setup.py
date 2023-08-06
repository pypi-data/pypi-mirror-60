import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mimosa-monomer",
    version="0.0.1",
    author="Dan Hampton",
    description="CLI for Stilt 2 database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'halo',
        'firebase-admin',
    ],
    entry_points={
        'console_scripts': [
            'mimosa=mimosa.main:main'
        ],
    },
)
