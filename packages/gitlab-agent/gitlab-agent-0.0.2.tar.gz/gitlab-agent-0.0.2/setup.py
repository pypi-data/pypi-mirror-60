import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gitlab-agent",
    version="0.0.2",
    author="Behan Remoshan BENET RUBAN",
    author_email="b.remoshan@gmail.com",
    description="A wrapper to use gitlab webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reevoremo/gitlab-agent",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
