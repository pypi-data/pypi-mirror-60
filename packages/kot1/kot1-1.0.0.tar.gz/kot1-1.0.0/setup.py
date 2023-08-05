from distutils.core import setup

# (Optional) Change the values that have a comment that starts with "# Change"
# (Must) Change the values that have a comment that starts with "# CHANGE"
setup(
  name = 'kot1',         # CHANGE to your package folder
  packages = ['kot1'],   # CHANGE to the same as 'name' above
  version = '1.0.0',      # Only change this to 1.x.0 when you release next versions
  license='MIT',        # More license options at https://help.github.com/articles/licensing-a-repository
  description = 'A thin wrapper of the openweatherapi for easy access to hourly weather forecast data.',   # Change this to describe the library shortly
  author = 'adi soadi',                   # CHANGE to your first and last name
  author_email = 'europa.geo@gmail.com',      # CHANGE to your email address
  url = 'https://github.com/adisoadi/kot1',   # CHANGE to the Github repository link
  download_url = 'https://github.com/adisoadi/kot1/archive/v1.0.0.tar.gz',    # CHANGE to the link of the download url
  keywords = ['weather', 'forecast', 'hourly'],   # Change the list values to search keywords that others can use to find your package
  install_requires=[],           # CHANGE the list values to library names that your package depends on
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Leave it as it is if you chose MIT above
    'Programming Language :: Python :: 3',      # Change the following to the Python versions the library supports
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',


  ],
)