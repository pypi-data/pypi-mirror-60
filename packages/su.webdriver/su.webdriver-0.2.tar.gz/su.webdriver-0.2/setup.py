from setuptools import setup, find_packages


VERSION = "0.2"

setup(
    name="su.webdriver",
    version=VERSION,
    url='https://bitbucket.org/zhaolins/su.webdriver',
    license='MIT',
    description="Webdriver with shortcuts.",
    author='Zhaolin Su',
    namespace_packages=['su'],
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'pytz',
        'su.password'
    ],
)
