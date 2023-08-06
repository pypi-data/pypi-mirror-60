import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='gymtools',  

     version='0.1',

     author="Nico Hähn",

     author_email="thomas.lenz@hauserlenz.com",

     description="A collection of tools that are useful for gyms.",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/tommylenz/gymtools",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )
