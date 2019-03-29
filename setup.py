import setuptools

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

with open("README.md", "r") as fh:
    long_description = fh.read()

reqs = parse_requirements("requirements.txt", session=False)
install_requires = [str(ir.req) for ir in reqs]

setuptools.setup(
    name="notion_log_exec",
    version="0.2.3",
    author="Maxwell Huang-Hobbs",
    author_email="mhuan13+pypy@gmail.com",
    description="Runs a command and reports the result back to a notion collection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adjective-object/notion-log-exec",
    install_requires=install_requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["notion-log-exec=notion_log_exec.__main__:main"]},
)
