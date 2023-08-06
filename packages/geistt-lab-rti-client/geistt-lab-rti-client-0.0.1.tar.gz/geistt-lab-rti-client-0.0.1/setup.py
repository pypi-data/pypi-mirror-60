import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
  name = 'geistt-lab-rti-client',         # How you named your package folder (MyLib)
  packages = ['geistt_lab_rti_client'],   # Chose the same as "name"
  version = '0.0.1',      # Start with a small number and increase it with every change you make
  license='Apache license 2.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'GEISTT Lab RTI Client',   # Give a short description about your library
  long_description=README,
  long_description_content_type="text/markdown",
  author = 'GEISTT AB',                   # Type in your name
  author_email = 'packages@geistt.com',      # Type in your E-Mail
  url = 'https://gitlab.com/geistt/lab/rti',   # Provide either the link to your github or to your website
  #download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['RTI'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'protobuf',
          'socketclusterclient',
          'emitter.py'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'License :: OSI Approved :: Apache Software License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)