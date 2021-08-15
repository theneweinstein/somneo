from setuptools import setup

setup(
    name = 'pysomneo',
    packages = ['pysomneo'],
    install_requires=['requests>=2.24.0','urllib3==1.26.5'],
    version = '0.1.14',
    description = 'A library to communicate with the API of Philips Somneo.',
    author='Ruud van der Horst',
    author_email='ik@ruudvdhorst.nl',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ' +
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ]
)
