try:
    from setuptools import setup, find_packages
except (ImportError, ModuleNotFoundError) as e:
    print("Please install setuptools and try again.\npip install setuptools")
    import sys
    sys.exit(1)
else:
    setup(
        name='ukbb_parser',
        author="Alyssa H. Zhu",
        description="ukbb_parser is a python-based parser for UK Biobank data",
        version='0.2',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'click',
            'html5lib',
            'numpy>=1.13.3',
            'pandas>=0.21.0'
        ],
        entry_points={
            'console_scripts': [
                'ukbb_parser = ukbb_parser.scripts.ukbb_parser:ukbb_parser',
                'ukbb_parser_test = ukbb_parser.tests.test_installation:main'
                ]
            }
    )
