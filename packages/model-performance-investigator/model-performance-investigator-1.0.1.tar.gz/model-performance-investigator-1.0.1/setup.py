import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="model-performance-investigator",
    version="1.0.1",
    author="Srikandan",
    author_email="kandan.sri15@gmail.com",
    description="Package give idea of a various models based on given data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/srikandan/model-evaluation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'tensorflow', 'keras', 'mxnet',
          'scikit-learn', 'numpy', 'pandas', 
          'statsmodels', 'matplotlib', 'xgboost',
          'scipy'
      ],
    python_requires='>=3.6',
)