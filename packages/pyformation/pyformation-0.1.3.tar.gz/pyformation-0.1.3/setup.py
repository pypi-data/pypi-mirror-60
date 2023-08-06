from setuptools import setup

setup(name='pyformation',
      version='0.1.3',
      description='CloudFormation eloquently expressed as Python',
      url='http://github.com/dennisvink/pyformation',
      author='Dennis Vink',
      author_email='dennis@drvink.com',
      license='MIT',
      packages=['pyformation', 'pyformation.utils', 'pyformation.bin', 'pyformation.templates'],
      install_requires=[
            'requests',
            'beautifulsoup4',
            'pyfiglet',
            'PyInquirer',
            'lxml',
            'jinja2',
            'GitPython',
            'python-dotenv',
            'moto'
      ],
      entry_points={
            'console_scripts': ['pyformation-admin=pyformation.bin.pyformation_admin:controller'],
      },
      zip_safe=False)
