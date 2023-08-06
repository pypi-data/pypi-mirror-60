import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="terraform-installer",
    version="1.0.1",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="install or upgrade the open source version of terraform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/shindagger/terraform-installer",
    packages=['terraforminstaller'],
    python_requires='>=3.6',
    install_requires= ['setuptools', 'string-color', 'beautifulsoup4', 'requests', 'tqdm', 'pywin32 ; platform_system=="Windows"'],
    entry_points={
        'console_scripts': ['terraform-installer=terraforminstaller.main:main', 'ti=terraforminstaller.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
