from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flashflood",
    version="0.4.3",
    author="Your Name",
    author_email="your.email@example.com",
    description="HTTP Load Testing Tool - Powerful, lightweight, and easy to use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flashflood",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "flashflood=flash:main",
        ],
    },
)
