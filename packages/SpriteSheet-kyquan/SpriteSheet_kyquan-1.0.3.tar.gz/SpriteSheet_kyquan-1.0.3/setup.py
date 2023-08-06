from setuptools import setup, find_packages

# import pipfile
# pf = pipfile.load('LOCATION_OF_PIPFILE')
# print(pf.data['default'])

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SpriteSheet_kyquan", # Replace with your own username
    version="1.0.3",
    author="Ho Ky Quan",
    author_email="quan.ho@f4.intek.edu.vn",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intek-training-jsc/sprite-sheet-kyquanlx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
