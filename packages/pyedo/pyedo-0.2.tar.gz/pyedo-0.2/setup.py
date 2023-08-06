import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='pyedo',  
     version='0.2',
     author="Comau",
     author_email="info@edo.cloud",
     description="This package contains the SDK to program COMAU e.DO robot with Python",
     long_description=long_description,
     url="https://github.com/Comau/pyedo",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: OS Independent",
     ],
 )
