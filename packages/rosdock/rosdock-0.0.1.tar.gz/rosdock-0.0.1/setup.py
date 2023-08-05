import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rosdock", # Replace with your own username
    version="0.0.1",
    author="Trinh Tran",
    author_email="trinhtran2151995@gmail.com",
    description="An utility scripts for wrapping ros catkin project and use it with docker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trinhtrannp/rosdock",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)