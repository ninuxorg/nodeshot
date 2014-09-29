from setuptools import setup, find_packages
from nodeshot import get_version


def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []

    for line in open('requirements.txt').readlines():
        # skip to next iteration if comment or empty line
        if line.startswith('#') or line == '' or line.startswith('http') or line.startswith('git'):
            continue

        # add line to requirements
        requirements.append(line)

    return requirements


setup(
    name='nodeshot',
    version=get_version(),
    description="Extensible Django web application for management of community-led georeferenced data.",
    long_description=open('README.rst').read(),
    author='Federico Capoano',
    author_email='nodeshot@ml.ninux.org',
    license='GPL3',
    url='https://github.com/ninuxorg/nodeshot',
    download_url='https://github.com/ninuxorg/nodeshot/releases',
    packages=find_packages(exclude=['docs', 'docs.*']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
    ],
    install_requires=get_install_requires(),
    scripts=['nodeshot/bin/nodeshot'],
)
