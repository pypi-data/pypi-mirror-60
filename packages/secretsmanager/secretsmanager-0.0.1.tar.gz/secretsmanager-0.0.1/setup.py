
import setuptools

setuptools.setup(
    name="secretsmanager",
    version="0.0.1",
    description='Used to get AWS by passing Secret name and Region',
    author='Sai Kumar',
    author_email='saikumar.p@talentas.in',
    license='MIT',
    long_description='Stores secrets of AWS',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)