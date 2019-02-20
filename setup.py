from setuptools import setup, find_packages
setup(
    name='ukbb_parser',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'html5lib',
        'numpy>=1.13.3',
        'pandas>=0.20.3'
    ],
    entry_points='''
        [console_scripts]
        ukbb_parser=ukbb_parser.ukbb_parser.scripts.ukbb_parser:ukbb_parser
    '''
)
