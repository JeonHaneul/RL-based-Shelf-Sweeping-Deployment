from pathlib import Path

from setuptools import find_packages, setup

package_name = 'control_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        *[("share/control_package/" + str(folder), [str(p) for p in folder.iterdir() if p.is_file()])
          for folder in Path("resource").rglob("*") if folder.is_dir()],
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/control_package/resource', ['resource/collected_data5.csv']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer="Haneul Jeon",
    maintainer_email="76903862+JeonHaneul@users.noreply.github.com",
    description='UR5e sweeping policy deployment, baseline controllers, and logging.',
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
