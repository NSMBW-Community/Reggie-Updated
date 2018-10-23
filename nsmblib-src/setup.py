from distutils.core import setup
from distutils.extension import Extension

setup(
  name='nsmblib',
  version='0.5',
  ext_modules=[
    Extension(
      'nsmblib',
      ['nsmblibmodule.c', 'list.c'],
    )
  ]
)
