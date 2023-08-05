from setuptools import find_packages, setup


setup(
    name='django-bs4',
    description='simple bootstrap4 support for django',
    version='0.0.1',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
