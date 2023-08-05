import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="throwbin",
    version="0.1",
    author="TriedGriefDev",
    description="API Wrapper for throwbin.io",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/triedgriefdev/throwbin",
    packages=setuptools.find_packages(),
    install_requires=["requests"]
)