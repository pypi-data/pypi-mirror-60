import setuptools


try:
    with open(os.path.join(base_path, 'requirements.txt'), encoding='utf-8') as f:
        REQUIREMENTS = f.read().split('\n')

except Exception:
    REQUIREMENTS = []


setuptools.setup(

     name='vfh',  

     version='0.1',

     scripts=['vfh/__init__.py','vfh/VFH.py'],
     author="Jubaer145",
     description="A python implementation of VFH pointcloud descriptor.",
     #long_description=long_description,
     long_description_content_type="text/markdown",
     url='',
     packages=setuptools.find_packages(),
     
     license = 'MIT',
     install_requires=REQUIREMENTS,
     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )