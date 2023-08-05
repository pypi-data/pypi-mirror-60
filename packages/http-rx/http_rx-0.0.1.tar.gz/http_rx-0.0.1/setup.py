import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as rf:
    requirements = rf.read().splitlines()

setuptools.setup(
    name='http_rx',
    version='0.0.1',
    author='Zachary King',
    author_email='kingzach77@gmail.com',
    description='Extensible HTTP health checker for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zcking/http_rx',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
    ],
    python_requires='>=3.4',
    install_requires=requirements,
)
