from setuptools import setup

setup(
	name='python-pique',
	version='1.0.0',
	license="MIT",
	description='Query JSON from the CLI using Python syntax',
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	author='http://github.com/Pebaz',
	url='http://github.com/Pebaz/pique',
    packages=['pique'],
	py_modules=['setup'],
    entry_points={
		'console_scripts' : [
			'pq=pique.pq:main'
		]
	}
)
