from setuptools import find_packages, setup

setup(name='bitpanda-secp256k1-hd-utils',
      version="0.0.5",
      packages=find_packages(),
      install_requires=['chainside-btcpy-multi>=0.2.78,<0.3.0'],
      description='Python tool for for tezos hd generation',
      author='Oskar Hladky',
      author_email='oskyks1@gmail.com',
      url='https://github.com/bitpanda-labs/secp256k1-hd-utils',
      python_requires='>=3',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ],
)
