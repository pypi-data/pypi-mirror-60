import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vox_cards", # Replace with your own username
    version="0.1.8",
    author="VoxLight",
    author_email="tkkt392@gmail.com",
    description="A dependancy free deck, card, and hand manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/voxlight/vox_cards",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)