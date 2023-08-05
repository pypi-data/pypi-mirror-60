from setuptools import setup

setup(name='colours_library',
      version='0.2',
      description='Colours library package',
      url='https://gitlab.bitcomp.intra/eryk_malczyk/colours_library.git',
      author='ErykM',
      author_email='eryk.malczyk@bitcomp.fi',
      license='some_license',
      packages=['colours_library'],
      install_requires=[
          'webcolors',
          'Pillow',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)