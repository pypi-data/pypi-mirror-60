import setuptools


setuptools.setup(
      name='AkerFlight',
      version='0.1',
      description='AutoFlightAware for Sunstates Aker',
      url='http://github.com/example',
      author='Matthew Turner',
      author_email='MatthewT@example.com',
      license='MIT',
      packages=setuptools.find_packages(),
      py_modules=["Flightaware"],
      install_requires=[
          'selenium',
          'openpyxl',
          'datetime'
      ],
      zip_safe=False)
