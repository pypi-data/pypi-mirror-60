import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nextcrop", # Replace with your own username
    version="0.0.12",
    author="Markus Leuthold",
    author_email="pypi@titlis.org",
    description="Crop and dewkew scanned images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={'console_scripts': ['nextcrop = nextcrop.main:main']},
    install_requires=['opencv-python', 'transitions', 'PySide2', 'simple_config', 'dependency_injector']
)
