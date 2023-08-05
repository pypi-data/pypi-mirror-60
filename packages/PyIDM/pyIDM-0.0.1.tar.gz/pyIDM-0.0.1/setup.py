import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyIDM", # Replace with your own username
    version="0.0.1",
    author="Mahmoud Elshahat",
    author_email="mahmoud_elshahhat@yahoo.com",
    description="download manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyIDM/pyIDM ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)