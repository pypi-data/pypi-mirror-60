from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='bcp-reader',
    version='0.1.1',
    description='Stream and convert BCP format files',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='http://github.com/drkane/bcp-reader',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='bcp convert csv',
    author='David Kane',
    author_email='david@dkane.net',
    license='MIT',
    packages=['bcp'],
    entry_points={
        'console_scripts': [
            'bcp=bcp.__main__:main',
        ],
    },
)
