from distutils.core import setup

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

setup(
  name='PygameFloatObjects',
  packages=['PygameFloatObjects', 'PygameFloatObjects.examples'],
  version='0.0.1',
  license='MIT',
  description='Improved Pygame objects to store float attributes',
  author='Pedro Azevedo',
  author_email='p.costa.azevedo@gmail.com',
  url='https://github.com/MrComboF10/PygameFloatObjects',
  install_requires=required,
  classifiers=[
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: pygame',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
