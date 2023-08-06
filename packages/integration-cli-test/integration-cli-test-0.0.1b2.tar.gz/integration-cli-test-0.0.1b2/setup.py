from setuptools import setup, find_packages

setup(
    name='integration-cli-test',
    version='0.0.1b2',
    packages=find_packages(),
    py_modules=['cli', '/smart_cli', '/smart_cli/generators'],
    install_requires=[
        'Click>=5.1',
        'Jinja2>=2.10.3',
    ],
    entry_points="""
        [console_scripts]
        integration=cli:smart_integration_cli
    """,
    include_package_data=True,
)