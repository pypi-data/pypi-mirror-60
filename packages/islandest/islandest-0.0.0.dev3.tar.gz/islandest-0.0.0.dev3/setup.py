from setuptools import setup, find_packages

setup(
    name="islandest",
    version='0.0.0_dev3',
    description='A command line tool to identify and annotate tRNA-targeting genomic islands',
    url='https://github.com/bhattlab/islandest',
    author="Matt Durrant",
    author_email="mdurrant@stanford.edu",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'biopython',
    ],
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'islandest = islandest.main:cli'
        ],
}
)
