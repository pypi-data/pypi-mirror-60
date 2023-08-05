import setuptools

def readme():
    with open('README.md') as f:
        README=f.read()
    return README

setuptools.setup(
    name="UCS633-topsis-SulbhMahajan",
    version="0.0.2",
    author="Sulbh Mahajan",
    author_email="sulbh579@gmail.com",
    description="A python package to implement topsis(MCDM)",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
	 "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #packages=["mypackage"],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=["pandas","numpy","scipy"],
    entry_points={
        "console_scripts":[
            "UCS633-topsis-Sulbh-101703569=mypackage.topsis:main",
        ]
    },
)