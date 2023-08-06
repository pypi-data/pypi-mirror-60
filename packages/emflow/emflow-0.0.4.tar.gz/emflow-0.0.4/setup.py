from setuptools import find_packages, setup

setup(
    name='emflow',
    version='0.0.4',
    author="DidaZxc",
    author_email="didazxc@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'flask_sqlalchemy',
        'dataclasses',
        'flask-httpauth',
        'flask_cors',
        'subprocess.run',
        'celery',
        'redis==3.3.11',
        'mrcfile',
        'pillow',
        'numpy',
        'scipy',
        'pyfunctional'
    ],
)
