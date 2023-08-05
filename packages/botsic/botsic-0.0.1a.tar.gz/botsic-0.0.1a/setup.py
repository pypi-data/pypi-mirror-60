from distutils.core import setup
setup(
    name='botsic',
    version='0.0.1a',
    description='Creates bots',
    url='https://github.com/ifosch/botsic',
    download_url='https://github.com/ifosch/botsic/archive/0.0.1a.tgz',
    author='Ignasi Fosch',
    author_email='natx@y10k.ws',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['botsic'],
    include_package_data=True,
    install_requires=['python-telegram-bot', ],
)
