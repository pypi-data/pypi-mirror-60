from setuptools import setup, find_packages

setup(name='cho_util',
      version='0.1.2',
      description='My python utilities',
      url='https://github.com/yycho0108/cho-util',
      download_url='https://github.com/yycho0108/cho-util/archive/stable.tar.gz',
      author='Yoonyoung (Jamie) Cho',
      author_email='jchocholate@gmail.com',
      keywords=['Transform', 'Math'],
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      scripts=['bin/pyhelp'],
      install_requires=[
          'numpy',
          'opencv-python',
      ],
      classifiers=[
          # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
          'Development Status :: 3 - Alpha',
          # Define that your audience are developers
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',   # Again, pick a license
          # Specify which pyhton versions that you want to support
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      )
