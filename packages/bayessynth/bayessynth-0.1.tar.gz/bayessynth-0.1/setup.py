from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()

setup(name='bayessynth',
      version='0.1',
      url='https://github.com/eliastuo/bayessynth',
      license='MIT',
      author='Elias Tuomaala',
      author_email='mail@eliastuomaala.com',
      description='Python implementation of Bayesian Synthetic Controls',
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires='>=3.7.4')
