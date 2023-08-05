import setuptools
from distutils.core import setup, Extension

skein_hash_module = Extension('mtns_skein_hash',
                               sources = ['skeinmodule.c',
                                          'skein.c'],
                               include_dirs=['.', './shacommon'])

setup (name = 'mtns_skein_hash',
       version = '1.0',
       package_data = {
        '': ['*.h']
        },
       license="MIT",
       maintainer='mtns dev',
       maintainer_email='git@omotenashicoin.site',
       author = 'mtns dev',
       author_email = 'git@omotenashicoin.site',
       description = 'Binding for OmotenashiCoin skein algo.',
       ext_modules = [skein_hash_module],
       url = 'https://github.com/omotenashicoin-project/mtns-skein-python.git',
       download_url = 'https://github.com/omotenashicoin-project/mtns-skein-python/archive/v1.0.tar.gz'
       )
