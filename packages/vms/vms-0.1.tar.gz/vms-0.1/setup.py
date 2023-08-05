from setuptools import setup

setup(
	name = 'vms',
	version = '0.1',
	install_requires = ['Click',],
	py_modules = ['vms'],
	entry_points = '''
	[console_scripts]
	vms=vms:vms
	rock=vms:pythonrocks
	
	
	'''
)