"""Portable deployment paths. Importing this module never connects to hardware."""

import os
from pathlib import Path


def workspace_root() -> Path:
    configured = os.environ.get('SWEEP_WORKSPACE')
    if configured:
        return Path(configured).expanduser().resolve()
    for parent in Path(__file__).resolve().parents:
        if (parent / 'src/control_package').is_dir() and (parent / 'src/base_package').is_dir():
            return parent
    raise RuntimeError('Set SWEEP_WORKSPACE to the deployment checkout.')


def configured_path(variable: str, default: str | Path) -> Path:
    path = Path(os.environ.get(variable) or default).expanduser()
    return (path if path.is_absolute() else workspace_root() / path).resolve()


def resource_path(package: str, relative: str) -> str:
    source = workspace_root() / 'src' / package / 'resource' / relative
    if source.exists():
        return str(source)
    try:
        from ament_index_python.packages import get_package_share_directory
        installed = Path(get_package_share_directory(package)) / 'resource' / relative
        if installed.exists():
            return str(installed)
    except (ImportError, LookupError):
        pass
    return str(source)


def policy_directory(default_run: str = '260311') -> str:
    return str(configured_path('SWEEP_POLICY_DIR', resource_path('control_package', default_run)))


def model_path() -> str:
    return str(configured_path('SWEEP_VISION_WEIGHTS', 'models/vision/best.pt'))


def calibration_path() -> str:
    return str(configured_path('SWEEP_CAMERA_CALIBRATION', 'config/calibration/orientation.yml'))


def log_path(relative: str) -> str:
    root = configured_path('SWEEP_LOG_DIR', 'logs')
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def robot_ip() -> str:
    value = os.environ.get('SWEEP_ROBOT_IP', '').strip()
    if not value:
        raise ValueError('Set SWEEP_ROBOT_IP to the intended robot before starting a controller.')
    return value
