import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ravan",
    version="0.0.1",
    # scripts = ['MIDI.py', 'mutils.py', 'rmidi.py', 'sound.py'],
    packages=['ravan'],
    author="rushike",
    author_email="rushike.ab1@gmail.com",
    description="Math Sequence to MIDI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rushike/ravan",
    install_requires=['numpy'],
    # packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)