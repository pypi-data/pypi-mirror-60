import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Watchmen',
    version='0.1.0',
    author='Procesor',
    author_email='jfortik@gmail.com',
    description='Comparing Image for Tesena',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/procesor2017/watchmen',
    packages=setuptools.find_packages(),
    install_requires=["Pillow", "numpy", "scikit-image", "imutils", "opencv-python", "robotframework"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.6',
)