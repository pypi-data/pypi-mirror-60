from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
    name='git-cd',
    version='0.0.1',
    author='Joseph Lam',
    author_email='mhlamaf@connect.ust.hk',
    description='A terminal tool for easy navigation to local git repository',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Doma1204/git-cd',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='git terminal',
    include_package_data=True,
    packages=["gitcd"],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts':[
            'gitcd=gitcd.cli_interface:cli'
        ],
    },
)
