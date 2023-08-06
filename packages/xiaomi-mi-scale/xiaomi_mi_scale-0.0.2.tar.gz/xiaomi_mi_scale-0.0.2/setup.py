import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xiaomi_mi_scale", # Replace with your own username
    version="0.0.2",
    author="Laurent Mahe",
    author_email="laurent.mahe@gmail.com",
    description="Libraries to read weight measurements from Xiaomi Mi Body Composition Scale (aka Xiaomi Mi Scale V2)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lolouk44/xiaomi_mi_scale",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)