#!/usr/bin/env python3
"""Inspect deployment source and required inputs without connecting to hardware."""
import argparse
import ast
import importlib.util
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def config_module():
    spec = importlib.util.spec_from_file_location('sweep_config', ROOT/'src/base_package/base_package/runtime_config.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['source', 'vision', 'opti', 'moveit'], default='source')
    parser.add_argument('--runtime', action='store_true', help='Also inspect Python/ROS package availability.')
    args = parser.parse_args()
    errors = []
    files = list((ROOT/'src').rglob('*.py')) + list((ROOT/'scripts').glob('*.py'))
    for file in files:
        try:
            ast.parse(file.read_text(encoding='utf-8-sig'), filename=str(file))
        except (SyntaxError, UnicodeError) as error:
            errors.append(f'{file.relative_to(ROOT)}: {error}')
    packages = list((ROOT/'src').rglob('package.xml'))
    for file in packages:
        try:
            ET.parse(file)
        except ET.ParseError as error:
            errors.append(f'{file.relative_to(ROOT)}: {error}')
    print(f'Checked {len(files)} Python files and {len(packages)} ROS package manifests.')
    config = config_module()
    if args.mode in ('vision','opti'):
        run = Path(config.policy_directory('260108' if args.mode == 'opti' else '260311'))
        required = [run/'exported/policy.pt', run/'params/env.yaml']
        if args.mode == 'vision':
            required += [Path(config.model_path()), Path(config.calibration_path())]
        for path in required:
            if not path.is_file():
                errors.append(f'Missing input: {path}')
        try:
            config.robot_ip()
        except ValueError as error:
            errors.append(str(error))
        tf_file = config.configured_path('SWEEP_TF_CONFIG','config/static_tf.json')
        try:
            json.loads(tf_file.read_text(encoding='utf-8'))
        except (OSError,ValueError) as error:
            errors.append(f'Invalid transform configuration: {error}')
    if args.mode == 'moveit':
        model = ROOT/'src/urdf_description/Universal_Robots_ROS2_Description/urdf/ur5e_with_gripper.urdf'
        if not model.is_file():
            errors.append(f'Missing original custom URDF: {model}')
    if args.runtime:
        modules = ['rclpy','tf2_ros','cv_bridge','numpy','torch','yaml','rtde_control','rtde_receive','loguru','pandas']
        if args.mode == 'vision':
            modules += ['cv2','ultralytics']
        for name in modules:
            if importlib.util.find_spec(name) is None:
                errors.append(f'Missing Python/ROS module: {name}')
        if importlib.util.find_spec('ament_index_python') is not None:
            from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
            expected = ['base_package','control_package','perception_package','custom_msgs','ur_description']
            if args.mode == 'vision':
                expected += ['lucid_camera_node']
            for name in expected:
                try:
                    get_package_share_directory(name)
                except PackageNotFoundError:
                    errors.append(f'ROS package is not available in the sourced environment: {name}')
        else:
            errors.append('ROS environment is not sourced or ament_index_python is unavailable.')
    if args.mode == 'vision':
        print('Camera integration is pending. File checks do not validate camera calibration or live topics.')
    for error in errors:
        print('ERROR:', error)
    if errors:
        return 1
    print('Requested checks passed. No hardware connection, ROS build, or policy execution was performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
