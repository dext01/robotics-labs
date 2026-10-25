from glob import glob

from setuptools import find_packages, setup

package_name = 'course_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='stepan',
    maintainer_email='nskyu2019@gmail.com',
    description='PR05 bringup',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_relay = course_bringup.pose_relay:main',
            'qos_listener = course_bringup.qos_listener:main',
        ],
    },
)
