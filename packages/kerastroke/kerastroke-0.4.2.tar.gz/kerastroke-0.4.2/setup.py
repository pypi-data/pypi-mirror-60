import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='kerastroke',
     version='0.4.2',
     scripts=['./kerastroke/__init__.py'] ,
     author="Charles Averill",
     author_email="charlesaverill20@gmail.com",
     description="A custom Keras callback to prevent overfitting",
     long_description=long_description,
     install_requires=['keras', 'numpy'],
   long_description_content_type="text/markdown",
     url="https://github.com/CharlesAverill/research",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
