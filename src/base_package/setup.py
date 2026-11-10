from setuptools import find_packages, setup
import os
from glob import glob

package_name = "base_package"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Haneul Jeon",
    maintainer_email="76903862+JeonHaneul@users.noreply.github.com",
    description="Shared ROS 2 managers, transforms, and deployment configuration.",
    license="Unspecified in upstream custom source",
    # tests_require=['pytest'],
    entry_points={
        "console_scripts": [],
    },
)
