
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
   from setupext_janitor import janitor
   CleanCommand = janitor.CleanCommand
except ImportError:
   CleanCommand = None

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

cmd_classes = {}
if CleanCommand is not None:
   cmd_classes['clean'] = CleanCommand

INSTALL_REQUIRES = [
    'powerline-status>=2.7',
    ]

def version():
    with open(os.path.abspath(__file__).replace('setup.py', 'version.meta'), 'r') as v:
        return v.read().replace('\n', '')

# Note: `setup_requires` will NOT be automatically installed on the system where the setup script is being run. 
# They are simply downloaded to the ./.eggs directory if they’re not locally available already.

setup(
    setup_requires=['setupext_janitor'], 
    cmdclass=cmd_classes,
    entry_points={
      # normal parameters, ie. console_scripts[]
      'distutils.commands': [
         ' clean = setupext_janitor.janitor:CleanCommand']
     },
    name='powerline-inject',
    version=version(),
    description='A powerline segment to show an ENV list with extra knobs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Scott MacGregor',
    author_email='smacgregor@d2iq.com',
    url='https://github.com/d2iq-shadowbq/powerline-inject',
    download_url='https://github.com/d2iq-shadowbq/powerline-inject/tarball/'+ version(),
    packages=['powerline_inject'],
    python_requires='>=3.6',
    install_requires=INSTALL_REQUIRES,
    license='Apache 2.0',
    keywords=['powerline','powerline_inject'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Terminals'
    ]
)
