from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_101703572",
    version="3.1.0",
    description="Python package to implement TOPSIS",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunvir72/Topsis",
    author="Sunvir Singh",
    author_email="sunvirsingh72@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101703572"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "topsis-101703572=topsis_101703572._init_:main",
        ]
    },
)
