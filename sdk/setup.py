from setuptools import setup, find_packages

setup(
    name="r0-engine",
    version="0.1.0",
    description="R₀ — Decision Physics Engine. Predicts whether products, habits, and decisions will survive.",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    author="Felix Wu",
    url="https://github.com/felixwulei/r0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],  # zero dependencies
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
)
