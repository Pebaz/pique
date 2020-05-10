from setuptools import setup

setup(
	name='python-pique',
	version='0.0.1',
	license="MIT",
	description='Process JSON from the CLI easily',
	author='http://github.com/Pebaz',
	url='http://github.com/Pebaz/pique',
    packages=['pique'],
    entry_points={
		'console_scripts' : [
			'pq=pique.pq:main'
		]
	}
)
