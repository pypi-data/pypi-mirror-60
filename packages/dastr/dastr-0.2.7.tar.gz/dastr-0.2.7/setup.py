
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
	name = 'dastr',
	packages = ['dastr'],
	version = '0.2.7',
	license = 'MIT',
	description = 'A tool for translating between scientific data structures',
	long_description=long_description,
    long_description_content_type='text/markdown',
	author = 'Isaac Kinley',
	author_email = 'isaac.kinley@gmail.com',
	url = 'https://github.com/kinleyid/dastr',
	download_url = 'https://github.com/kinleyid/dastr/archive/v_027.tar.gz',
	keywords = ['data', 'structure', 'translator'],
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python'
	],
)