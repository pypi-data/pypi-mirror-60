import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

packages = setuptools.find_packages()

setuptools.setup(
    name='python_eloqua_wrapper',
    version='0.0.8',
    author="Tim Sawicki",
    author_email="tsawicki@redhat.com",
    description="A wrapper for Eloqua's HTTP REST API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.corp.redhat.com/mkt-ops-de/python-eloqua-wrapper.git",
    packages=packages,
    install_requires=["requests"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
