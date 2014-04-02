from setuptools import setup, find_packages
from nodeshot import get_version


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
        'License :: OSI Approved :: GPL3 License',
        'Operating System :: Linux/Unix',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)
