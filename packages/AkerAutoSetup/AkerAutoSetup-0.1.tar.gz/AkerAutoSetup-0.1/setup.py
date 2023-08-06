import setuptools


setuptools.setup(
      name='AkerAutoSetup',
      version='0.1',
      description='AutoClose for Sunstates Aker',
      url='http://github.com/example',
      author='Matthew Turner',
      author_email='MatthewT@example.com',
      license='MIT',
      packages=setuptools.find_packages(),
      py_modules=["Autoclose"],
      install_requires=[
          'pyautogui',
          'pywin32'
      ],
      zip_safe=False)
