from setuptools import setup, find_packages

setup(
    name='pickaa',
    version='1.0.0',
    author='Josh Ike',
    author_email='joshike.no@gmail.com',
    description='Random Argument Picker',
    url='https://github.com/joshikeno/pickaa',
    install_requires=['click'],
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        pickaa=pickaa:cli
    """
)
