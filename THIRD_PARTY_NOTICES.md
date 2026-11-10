# Source provenance and licenses

This distribution is maintained by Haneul Jeon. Maintenance and packaging do not replace the original source authorship.

| Component | Source revision | Local location |
| --- | --- | --- |
| Deployment project | [Holiclife-KTH/Robust-Sweeping-in-Cluttered-Shelves](https://github.com/Holiclife-KTH/Robust-Sweeping-in-Cluttered-Shelves/tree/d5d52f8d511800210b7bdbab3fd75150b59a3b41), `d5d52f8d511800210b7bdbab3fd75150b59a3b41` | Custom ROS packages |
| UR description | [UniversalRobots/Universal_Robots_ROS2_Description](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description/tree/31a04ce759855bae6ce14c6c0499d3c3c0a1ddf5), `31a04ce759855bae6ce14c6c0499d3c3c0a1ddf5` | `src/urdf_description/Universal_Robots_ROS2_Description` |
| Robotiq packages | [PickNikRobotics/ros2_robotiq_gripper](https://github.com/PickNikRobotics/ros2_robotiq_gripper/tree/e78b482c98a58cc3a91ab14c9dd7db3e296c1088), `e78b482c98a58cc3a91ab14c9dd7db3e296c1088` | `src/urdf_description/ros2_robotiq_gripper` |
| POE solver | [Holiclife-KTH/POE_Robot_Kinematics_Solver](https://github.com/Holiclife-KTH/POE_Robot_Kinematics_Solver/tree/ef1878ec63bad7f1e5f63a48b85a3de3ceb382de), `ef1878ec63bad7f1e5f63a48b85a3de3ceb382de` | `src/control_package/control_package/POE_Robot_Kinematics_Solver` |

The original POE gitlink `ecfee948ddd12bcf9ea9f9a6e19c70843b9e2daf` was unavailable. The listed replacement includes the expected `RobotKinematicsPOE`, `UR5E_CONFIG`, and `IKResult` interfaces. Its numerical behavior must still be validated for the experiment. A package initializer and missing annotation aliases were added without changing its mathematical operations. Its generated editor settings were omitted.

UR and Robotiq source files retain their original licenses and notices. The UR repository distinguishes BSD-3-Clause content from newer robot meshes covered by its graphical-documentation terms. See the bundled UR README and per-directory notices. No upstream author or mesh attribution has been relabeled.

The custom deployment and POE sources do not supply a complete project-wide license declaration. Their original author fields are retained, including the MoveIt configuration author. This distribution does not invent a new license for that source. NatNet headers and samples retain their NaturalPoint notices. Python/ROS packages and proprietary SDKs are separate dependencies with their own terms.

The camera submodule is not bundled in this stage. No unpublished manuscript or research-paper citation is included.
