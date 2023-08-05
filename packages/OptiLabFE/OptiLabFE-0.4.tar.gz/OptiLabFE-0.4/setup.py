import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='OptiLabFE',
     version='0.4',
     author="Parallel team",
     author_email="fede.campe@gmail.com",
     description="Front-end for Parallel-OptiLab package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://www.parallel-ai.com",
     packages=['optilabfe'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
