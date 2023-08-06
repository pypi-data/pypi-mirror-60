import setuptools
from pdfsearcher import __version__

# to build and install:
# python setup.py
# pip install dist/mlpipeline-*-py3-none-any.whl

setuptools.setup(
    name="pdfsearcher",
    version=__version__,
    author='Ahmed Shariff',
    author_email='shariff.mfa@outlook.com',
    packages=setuptools.find_packages(),
    description='',
    long_description=open('README.rst').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ahmed-shariff/mlpipeline',
    install_requires=['pdfminer.six', 'click', 'tqdm'],
    entry_points={
        'console_scripts': [
            # 'mlpipeline_old=mlpipeline._pipeline:main',
            # '_mlpipeline_subprocess_old=mlpipeline._pipeline_subprocess:main',
            # 'mlpipeline=mlpipeline._cli:cli'
            'pdf-searcher=pdfsearcher._cli:cli'
            ]
        },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ]
)
