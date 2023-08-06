import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='gymtools',  

     version='0.2',
     

     author="Nico Hähn",

     author_email="nicohaehn@t-online.de",
     

     description="A collection of tools that are useful for gyms.",

     long_description=long_description,

     long_description_content_type="text/markdown",
     

     url="https://github.com/tommylenz/gymtools",
     license="MIT",

     packages=setuptools.find_packages(),
     

     classifiers=[
         "Development Status :: 3 - Alpha",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],

     keywords="gymtools gym bmi",

     python_requires=">=3",

 )
