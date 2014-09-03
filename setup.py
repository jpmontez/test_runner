from setuptools import setup


# def readme():
#     with open('README', 'r') as f:
#         return f.read()


setup(
    name='test-runner',
    version='1.0',
    description='Execute OpenStack frameworks',
    # long_description=readme(),
    url='https://github.com/jpmontez/test-runner',
    author='Julian Montez',
    author_email='julian.montez@rackspace.com',
    license='MIT',
    packages=['test-runner'],
    entry_points={
        'console_scripts': [
            'test-runner = test_runner.executable:main',
        ]
    },
    install_requires=[
        'argcomplete',
        'argh',
        'jinja2',
        'nose-exclude',
        'nose-json',
        'python-keystoneclient',
        'python-neutronclient',
        'python-novaclient'
    ],
    zip_safe=False
)
