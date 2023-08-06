from setuptools import setup, find_packages

setup(
    name='pythonlogbook',
    version='1.2.3',
    description='A simple logbook made with python',
    url='https://github.com/lukew3/logbook',
    author='Luke Weiler',
    author_email='lukew25073@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={
	   'console_scripts': [
            'newlog=pythonlogbook.addentry:main', #add combine logs later
            'combinelogs=pythonlogbook.combineLogs:main',
	   ],
    },
)
