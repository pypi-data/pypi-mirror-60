from setuptools import setup

setup(name='regindexer',
      version='0.6.1',
      description='Tool for creating an index of a container registry',
      url='https://pagure.io/regindexer',
      author='Owen Taylor',
      author_email='otaylor@redhat.com',
      license='MIT',
      packages=['regindexer'],
      include_package_data=True,
      install_requires=[
          'click',
          'fedmsg',
          'PyYAML',
          'requests',
          'six',
      ],
      entry_points= {
          'console_scripts': [
              'regindexer=regindexer.cli:cli',
              'regindexer-daemon=regindexer.daemon:main',
          ],
      })
