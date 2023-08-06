from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='image_croquis',
    url='https://github.com/nagavenkateshgavini/image_croquis',
    author='Naga Venkatesh Gavini',
    author_email='',
    # Needed to actually package something
    packages=['image_croquis'],
    # Needed for dependencies
    install_requires=['opencv-python'],
    # *strongly* suggested for sharing
    version='0.0.4',
    # The license can be anything you like
    license='MIT',
    description='An example of a python package with a basic use case',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
    entry_points = {
        'console_scripts':[
            'image_croquis = image_croquis.image_croquis:main',
        ]
    }
)
