from distutils.core import setup
setup(
  name = 'sgrep',         # How you named your package folder (MyLib)
  packages = ['sgrep'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='LGPL',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'polyglot AST pattern search',   # Give a short description about your library
  author = 'Yoann Padioleau',                   # Type in your name
  author_email = 'sgrep@r2c.dev',      # Type in your E-Mail
  url = 'https://github.com/returntocorp/sgrep',   # Provide either the link to your github or to your website
  keywords = ['sgrep'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pyyaml',
          'requests'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
