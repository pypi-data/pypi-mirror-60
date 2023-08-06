import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyeca",
    version="0.0.1",
    author="John Viloria Amaris",
    author_email="jviloriaa-est@electricaribe.co",
    description="ECA Functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/packagename",
    packages=setuptools.find_packages(),
    install_requires  = ['pathlib','datetime'], # List all your dependencies inside the list
    license = 'MIT'
)