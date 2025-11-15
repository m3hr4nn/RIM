from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="redfish-management-suite",
    version="1.0.0",
    author="m3hr4nn",
    author_email="",
    description="Professional DMTF Redfish-compliant server health monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m3hr4nn/RIM",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "redfish-health-check=redfish_management_suite.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "redfish_management_suite": ["templates/*.xlsx", "web/*"],
    },
)
