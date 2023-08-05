import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shholiday",
    version="0.0.1",
    license='MIT',
    author="league3236",
    author_email="league3236@gmail.com",
    description="Check if the current date is a holiday in Korea.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/league3236/shholiday",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)