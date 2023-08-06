import setuptools

setuptools.setup(
    name="turkishfullnamegenerator", 
    version="0.0.3",
    author="anilkay",
    author_email="aanilkay@gmail.com",
    description="Generate full turkish names ",
    url="https://github.com/anilkay/Turkish-FullName-Generator",
    packages=["turkishfullname"],
    keywords = ['name generator', 'turk', 'turkish'], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)