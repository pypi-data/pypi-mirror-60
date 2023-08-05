import setuptools

with open("README.md", "r") as file_handler:
    long_description = file_handler.read()

setuptools.setup(
    name='easy-ansi',
    version='0.0.0',
    author='Joey Rockhold',
    author_email='joey@joeysbytes.net',
    description='A library to make it easy to use ANSI escape sequences within your Python program.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url='https://gitlab.com/joeysbytes/easy-ansi',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Terminals"
    ],
    python_requires='>=3.5'
)
