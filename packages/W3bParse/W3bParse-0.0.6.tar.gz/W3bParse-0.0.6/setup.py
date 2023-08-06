import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="W3bParse", # Replace with your own username
    version="0.0.6",
    author="Colby Sehnert",
    author_email="colbysehnert@gmail.com",
    description="A simple web parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/exampleproject",
    keywords='web-parser, development',
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
	'Programming Language :: Python',
    ],
    python_requires='>=3.8',
)
