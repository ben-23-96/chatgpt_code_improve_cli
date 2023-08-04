from setuptools import setup, find_packages

setup(
    name="gpt-code-edit",
    version="1.0.6",
    packages=find_packages(),

    # Metadata
    author="Ben Speakman",
    author_email="benspeakman23@yahoo.com",
    description="A command line interface that allows you to target specific functions, classes, or methods in a file and use chatgpt to perform several edits including refactoring, adding comments, adding docstrings, or adding error handling.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ben-23-96/chatgpt_code_improve_cli",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],

    # Dependencies
    install_requires=[
        "aiohttp==3.8.4",
        "markdown-it-py==3.0.0",
        "redbaron==0.9.2",
        "tqdm==4.65.0",
    ],

    # Entry points
    entry_points={
        "console_scripts": [
            "gpt=chatgpt_cli.main:main",
        ],
    },
)
