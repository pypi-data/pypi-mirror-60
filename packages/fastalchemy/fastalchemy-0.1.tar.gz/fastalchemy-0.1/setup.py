from distutils.core import setup
setup(
    name='fastalchemy',
    packages=['fastalchemy'],
    version='0.1',
    license='MIT',
    description='A SQLAlchemy middleware for FastAPI',
    author='Joseph Kim',
    author_email='cloudeyes@gmail.com',
    url='https://github.com/cloudeyes/fastalchemy',
    download_url='https://github.com/cloudeyes/fastalchemy/archive/v0.1.tar.gz',
    keywords=['fastapi', 'middleware', 'sqlalchemy', 'plugin'],
    install_requires=[
        'fastapi', 'sqlalchemy',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
