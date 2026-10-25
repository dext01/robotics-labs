from setuptools import find_packages, setup

package_name = 'patrol'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='stepan',
    maintainer_email='nskyu2019@gmail.com',
    description='Patrol node for turtlesim',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'patrol_node = patrol.patrol_node:main',
        ],
    },
)
