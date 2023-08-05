from setuptools import setup, find_packages
import codecs

description = 'Simple ticker for use on linux platform with max ' \
              'resolution of 1ms'
with codecs.open('./README.rst', encoding='utf-8') as readme_md:
    long_description = readme_md.read()

setup(
    name='linux_ticker',
    version='0.0.12',
    author='Ishwor Gurung',
    author_email='me@ishworgurung.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/ishworgurung/linux-ticker',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=False,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    maintainer='Ishwor Gurung',
    maintainer_email='me@ishworgurung.com',
    python_requires='>=3.6',
)
