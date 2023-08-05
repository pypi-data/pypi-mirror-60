import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

with open("version.txt", "r") as fh:
  version = fh.read()


install_requires = []
with open("requirements.txt", "r") as fh:
  for x in fh:
    install_requires.append(x)


setuptools.setup(
    name="vouched-python",
    version=version,
    author="John Cao",
    author_email="cao@vouched.id",
    description="Vouched Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vouched/vouched-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Academic Free License (AFL)",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires
)
