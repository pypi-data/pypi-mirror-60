from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pytable-console',
      version='1.0',
      url='https://github.com/McFinnious/pytable/edit/master/README.md',
      license=open('LICENSE').read(),
      author='McFinnious',
      author_email='finn.custard@gmail.com',
      description='Create and edit python tables.',
      packages=['pytable'],
      long_description=open('README.md').read(),
      zip_safe=False)
