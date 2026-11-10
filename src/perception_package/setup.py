from setuptools import find_packages, setup

package_name = 'perception_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer="Haneul Jeon",
    maintainer_email="76903862+JeonHaneul@users.noreply.github.com",
    description='Object detection and RGB-point-cloud target localization.',
    license='Unspecified in upstream custom source',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
