import setuptools

setuptools.setup(
    name="hello-kjmerf",
    version="0.0.6",
    author="Kevin Merfeld",
    author_email="kevinjmerfeld@gmail.com",
    description="A package that says hello to kjmerf",
    long_description='This package says hello to kjmerf!',
    long_description_content_type="text/markdown",
    url="https://github.com/kjmerf/hello_kjmerf",
    download_url="https://github.com/kjmerf/hello_kjmerf/archive/v_0_0_6.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
