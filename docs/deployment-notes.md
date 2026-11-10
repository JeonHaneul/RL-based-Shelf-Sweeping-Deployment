# Deployment notes

## Policy interface

| Observation indices | Values |
| --- | --- |
| 0-5 | Six arm positions minus the saved default positions |
| 6-7 | Gripper-state proxy selected from the seventh action sign |
| 8-13 | Six arm velocities |
| 14-20 | Seven-value stored action history |
| 21-23 | Target position in the robot base frame |
| 24 | Target width |
| 25-31 | TCP position and quaternion, ordered x/y/z/w/x/y/z |
| 32-34 | Goal position in the robot base frame |

The policy output is scaled by 0.5 and offset by the saved default joint positions. Only six outputs are sent to the arm. The original left sweep, 0.18 m goal displacement, hard-coded shelf-height calculation, input filtering, action-history update order, and joint command smoothing are retained. Matching vector dimensions alone does not prove compatibility with a newly trained policy.

## Packaging changes

- Replaced personal machine paths with repository-relative defaults and `SWEEP_*` settings. Saved training YAML snapshots keep their numeric parameters but use portable placeholders for unused simulator paths.
- Changed package maintainer metadata to Haneul Jeon. Explicit original author fields, SDK notices, and upstream licenses remain intact.
- Expanded UR and Robotiq submodules at their recorded revisions, including meshes. Replaced the unavailable POE revision with the recorded available revision and included a package initializer.
- Corrected legacy imports to use the common service managers and UNO modules that exist in this checkout.
- Included saved resource directories in the installed control package and declared ROS package dependencies.
- Corrected ROS argument filtering and the DRL TF timeout's duration type.
- Required both joint and TCP state, plus target width, before policy observations are formed. The vision loop now waits for missing inputs and checks TCP availability before updating it.
- Loaded TorchScript on CPU in evaluation mode, consistent with NumPy-based action conversion.
- Corrected the vision controller's shutdown ordering so the spin thread does not block indefinitely after an episode. Stop and logger-stop requests precede ROS shutdown.
- Moved the unchanged static transform values into `config/static_tf.json`.

These changes have isolated source/unit checks. They are not a physical robot validation or an implementation of a certified safety controller.

## Optional modes and missing inputs

| Mode | Entry point | Additional requirements |
| --- | --- | --- |
| Vision DRL | `control_package.DRL.run_task_with_vision` | TorchScript policy, matching env YAML, detector weights, camera driver, calibration, robot/TF setup |
| OptiTrack DRL | `control_package.DRL.run_task_with_opti` | Matching policy, Motive/NatNet stream and configured transforms |
| UNO-Push | `control_package.uno_push.uno_mpc_vision` or `uno_mpc_opti` | Baseline Python dependencies and calibrated tracking/control setup |
| Human-in-the-loop | `control_package.HITL.run` | MoveIt services and the original custom robot/gripper description |

`ur5e_gripper_moveit_config/config/ur5e.urdf.xacro` references `ur_description/urdf/ur5e_with_gripper.urdf`, which is absent from both the main source and the pinned official UR description. The original gripper mount geometry cannot be reconstructed from that reference alone. Supply the matching description before launching the MoveIt examples.

`base_package/launch/servo.launch.py` retains an incomplete Panda-derived example and is not the UR5e deployment entry point. Do not use it as the documented DRL startup procedure. The older `DRL/path_generator.py` defaults to a 251210 policy directory that was not included. Optional modes have not been runtime-validated.

The repository has no custom policy weights, YOLO weights, or camera calibration. The original NatNet headers and Python samples are present, but a complete native NatNet SDK/library is not included.
