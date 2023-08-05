from distutils.core import setup
setup(
  name = 'ArabicPreProcessing',         # How you named your package folder (MyLib)
  packages = ['ArabicPreProcessing'],   # Chose the same as "name"
  version = '0.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Arabic PreProcessing Functions that must applied before run any ML model.',   # Give a short description about your library
  author = 'Rashed Sabra',                   # Type in your name
  author_email = 'rashed.sabra@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/rashed963',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/rashed963/ArabicPreProcessing/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['NLP', 'pre-processing', 'Arabic'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'nltk',
		  'regex',
    
    
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',
  ],
)
