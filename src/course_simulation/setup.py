import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'course_simulation'


def tree(src, dst):
    """Install every file under ``src`` keeping the relative layout."""
    out = []
    for root, _dirs, files in os.walk(src):
        if files:
            out.append((os.path.normpath(os.path.join('share', package_name, dst, os.path.relpath(root, src))),
                        [os.path.join(root, f) for f in files]))
    return out


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
    ] + tree('models', 'models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='stepan',
    maintainer_email='nskyu2019@gmail.com',
    description='Course simulation',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ackermann_adapter = course_simulation.ackermann_adapter:main',
            'odom_adapter = course_simulation.odom_adapter:main',
            'drive_source = course_simulation.drive_source:main',
        ],
    },
)
