import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyForce01",
    version="1.0.6",
    author="Quantum_Wizard",
    author_email="minecraftcrusher100@gmail.com",
    description="""You already know.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GrandMoff100/MathFunctions",
    packages=setuptools.find_packages(include=['PyForce01','selenium','keyboard','mouse']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
