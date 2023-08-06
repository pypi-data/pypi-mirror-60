from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='AFE',
    version='2020.01.30',
    description='Accelerometer Feature Extractor',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://bitbucket.org/atpage/afe',
    author='Alex Page',
    author_email='alex.page@rochester.edu',
    # classifiers=[
    #     'License :: OSI Approved :: MIT License',
    #     'Programming Language :: Python :: 3',
    # ],
    python_requires='>=3.0',
    packages=find_packages(exclude=['tests']),
    install_requires=['numpy', 'scipy', 'pandas', 'actigraph'],
    keywords='accelerometer acceleration gyroscope machine learning features',
    # package_data={},
    # entry_points={},
    # zip_safe=False
)
