from setuptools import setup, find_packages
from setuptools.command.test import test

from nodeshot import get_version


#class TestCommand(test):
#    def run(self):
#        from tests.runtests import runtests
#        runtests()


setup(
    name='nodeshot',
    version=get_version(),
    description="Extensible Django web application for management of community-led georeferenced data.",
    long_description=open('README.md').read(),
    author='Federico Capoano',
    author_email='nemesis[at]ninux[dot]org',
    license='GPL3',
    url='https://github.com/nemesisdesign/nodeshot',
    packages=find_packages(exclude=['docs', 'docs.*']),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL3 License',
        'Operating System :: Linux/Unix',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
    #cmdclass={"test": TestCommand},
)