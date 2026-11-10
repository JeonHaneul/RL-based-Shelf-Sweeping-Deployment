# RL-based Shelf Sweeping Deployment

ROS 2 software for deploying a learned shelf-sweeping policy on a UR5e. RGB and point-cloud observations provide the target position and width, while the exported policy produces arm joint-position commands sent through `ur_rtde`.

This is a **separate real-robot deployment repository**. Simulation training is maintained in [RL-based-Shelf-Sweeping](https://github.com/JeonHaneul/RL-based-Shelf-Sweeping). The repositories are not merged, and a policy must be exported and checked against this deployment observation/action layout before use.

## Workflow

| Stage | Implementation |
| --- | --- |
| Sensing | RGB image and colored point cloud from the camera stack |
| Detection | YOLO bounding boxes and target class selection |
| Localization | Project point-cloud points into the image, estimate target position and width, and transform into the robot base frame |
| Policy input | 35 values containing joint state, action history, target geometry, TCP pose, and goal |
| Control | TorchScript inference, six arm position targets, and RTDE `servoJ` commands |
| Recording | ROS logging services and CSV files for trajectories and object movement |

The source also contains OptiTrack-based DRL evaluation, UNO-Push, and human-in-the-loop code. These are separate experimental entry points, not additional stages of the vision-based DRL loop.

## Code structure

| Directory | Role |
| --- | --- |
| `src/base_package/` | Shared ROS managers, transforms, and portable deployment paths |
| `src/control_package/control_package/DRL/` | Policy loading, observation construction, vision/OptiTrack controllers, and logging |
| `src/control_package/control_package/uno_push/` | Data collection and learned-model MPC baseline |
| `src/control_package/control_package/HITL/` | Human-in-the-loop comparison code |
| `src/control_package/resource/` | Saved training configuration snapshots and baseline CSV data |
| `src/perception_package/` | Detection, target localization, and NatNet Python clients |
| `src/custom_msgs/` | Bounding-box messages and logging service definitions |
| `src/urdf_description/` | Vendored UR description and Robotiq packages, including meshes |
| `src/ur5e_gripper_moveit_config/` | Original MoveIt configuration, with a missing custom URDF dependency |
| `config/` | Deployment settings and recorded static transforms |
| `scripts/` | Checks that do not connect to or move a robot |

UR and Robotiq sources are included as ordinary files at the original pinned revisions. The POE kinematics solver is also included locally. Its original pinned revision was unavailable, so an available revision is recorded in [third-party notices](THIRD_PARTY_NOTICES.md). No Git submodule initialization is needed. The camera repository is pending separate integration.

## Installation

The original stack targets Ubuntu 22.04, ROS 2 Humble, and Python 3.10. Install [ROS 2 Humble](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html) first, then use a separate workspace from the Isaac Lab training checkout:

```bash
git clone https://github.com/JeonHaneul/RL-based-Shelf-Sweeping-Deployment.git
cd RL-based-Shelf-Sweeping-Deployment
source /opt/ros/humble/setup.bash
sudo apt install python3-colcon-common-extensions python3-rosdep python3-pip \
  ros-humble-ur ros-humble-moveit ros-humble-cv-bridge ros-humble-tf2-geometry-msgs
python3 -m pip install -r requirements.txt
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
export SWEEP_WORKSPACE="$PWD"
```

On a fresh ROS installation, initialize rosdep once with `sudo rosdep init` before `rosdep update`. `requirements.txt` is a dependency list, not a hardware-validated lockfile. Install a PyTorch version compatible with the exported policy. The training and deployment Python environments are separate.

## Files and settings to provide

The original source contains configuration snapshots, **but no trained policy, YOLO weights, or camera calibration file**.

| Input | Expected layout or setting |
| --- | --- |
| Policy export | `SWEEP_POLICY_DIR/exported/policy.pt` and matching `SWEEP_POLICY_DIR/params/env.yaml` |
| Detector weights | `SWEEP_VISION_WEIGHTS`, default `models/vision/best.pt` |
| Camera calibration | `SWEEP_CAMERA_CALIBRATION`, default `config/calibration/orientation.yml` |
| Robot address | `SWEEP_ROBOT_IP`, explicitly configured before starting a controller |
| Static transforms | `SWEEP_TF_CONFIG`, default `config/static_tf.json` |
| Logs | `SWEEP_LOG_DIR`, default `logs/` |

Copy `config/deployment.env.example` to `config/deployment.env`, edit its values, then load it in each terminal:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export SWEEP_WORKSPACE="$PWD"
source config/deployment.env
python3 scripts/check_setup.py --mode vision --runtime
```

The check reports missing files and dependencies without connecting to hardware. The existing transform values and shelf height are specific to the original experiment and must match the actual setup. See [camera integration](docs/camera-integration.md) for topics, frames, and calibration keys.

## Vision-based DRL execution

Use separate terminals with the same environment settings. Start the robot-state driver and calibrated transforms, then the camera and perception nodes. The [UR driver startup guide](https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_robot_driver/ur_robot_driver/doc/usage/startup.html) describes the robot-side setup.

```bash
# Robot state / TF infrastructure
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur5e robot_ip:="$SWEEP_ROBOT_IP"
ros2 launch base_package static_tf.launch.py

# Camera command used by the original stack, available after camera integration
ros2 run lucid_camera_node lucid_node

# Separate terminals
python3 -m perception_package.segmentation
python3 -m perception_package.pose_estimate --target_cls Can_1

# Optional logger in another terminal
python3 -m control_package.DRL.drl_logging --episode_num 1

# Starts the physical robot controller
python3 -m control_package.DRL.run_task_with_vision --episode_num 1
```

The final command connects to RTDE and moves the arm to its initial posture during initialization. It is not a preview command. The motion loop uses direct RTDE control, so do not command the same arm simultaneously through another controller. Camera startup remains pending until the separate camera repository and its SDK are installed.

## Policy compatibility and validation

The controller expects **35 observation values and seven policy outputs**. It sends only the first six outputs as arm targets. The seventh value is used in the observation history and does not directly actuate the physical gripper in this DRL controller. A training checkpoint such as `model_*.pt` is not the TorchScript `exported/policy.pt` expected here.

The original control loop requests 100 Hz, with policy inference scheduled using the saved decimation. This is not a measured real-time guarantee. Observation order, joint order, coordinate frames, gripper-state representation, and timing must be checked when exporting a new policy from the separate training repository.

```bash
python3 scripts/check_setup.py
python3 -m unittest discover -s tests -v
```

Source checks and isolated unit tests are provided. ROS compilation, model inference, and physical robot execution have not been validated in this distribution. [Deployment notes](docs/deployment-notes.md) record the packaging changes and remaining dependencies for the optional experimental modes.

Maintained by [Haneul Jeon](https://github.com/JeonHaneul). Original authorship and third-party licenses are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
