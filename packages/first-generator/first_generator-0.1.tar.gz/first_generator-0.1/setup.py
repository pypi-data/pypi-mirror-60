import setuptools

setuptools.setup(
    name='first_generator',
    version='0.1',
    description='FIRST is Finding Interesting Stories about Students',
    url='',
    author='Ahmad Al-Doulat',
    author_email='adoulat@uncc.edu',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_version='>=3.6',
    include_package_data=True,
)
