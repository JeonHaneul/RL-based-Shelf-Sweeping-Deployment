"""Publish calibrated transforms from SWEEP_TF_CONFIG or config/static_tf.json."""
import json
from launch import LaunchDescription
from launch_ros.actions import Node
from base_package.runtime_config import configured_path


def generate_launch_description():
    path = configured_path('SWEEP_TF_CONFIG', 'config/static_tf.json')
    transforms = json.loads(path.read_text(encoding='utf-8'))
    return LaunchDescription([
        Node(package='tf2_ros', executable='static_transform_publisher',
             name=item['name'], arguments=item['arguments'])
        for item in transforms
    ])
