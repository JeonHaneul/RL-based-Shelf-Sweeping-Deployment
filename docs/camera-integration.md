# Camera integration

Build the [Shelf-Sweeping Camera Kit](https://github.com/JeonHaneul/RL-based-Shelf-Sweeping-Camera-Kit#build-the-camera-workspace) in a separate ROS 2 Humble workspace. Its `lucid_camera_node` publishes a Triton image in `triton_camera` and a colored Helios2 point cloud in `helios_camera`. The deployment subscribes to the following topics.

| Interface | Type | Default |
| --- | --- | --- |
| RGB input | `sensor_msgs/Image`, decoded as BGR8 | `/triton/image_raw`, overridden with `SWEEP_RGB_TOPIC` |
| Point-cloud input | `sensor_msgs/PointCloud2` | `/helios/pointcloud_rgb`, overridden with `SWEEP_POINTCLOUD_TOPIC` |
| Detected boxes | `custom_msgs/BBoxMultiArray` | `/segmentation/bboxes` |
| Target position | `geometry_msgs/PoseStamped` | `/pose_estimate/position` |
| Target width | `std_msgs/Float32` | `/pose_estimate/width` |

`pose_estimate.py` expects an OpenCV calibration file containing `cameraMatrix`, `distCoeffs`, `rotationVector`, and `translationVector`. Point-cloud coordinates, projection units, image resolution, distortion model, and frame names must agree with that calibration.

The recorded transform chain is `base_link -> opti_world -> triton_camera -> helios_camera`. The TCP is attached to `tool0_controller`. The numbers in `config/static_tf.json` are preserved experiment values, not calibration results for a new robot or camera position. Replace that file or set `SWEEP_TF_CONFIG` after calibration.

Set `SWEEP_CAMERA_CALIBRATION` and the driver’s `orientation_file` to the same file. The kit publishes XYZ in metres. The pose estimator converts those points to millimetres for projection, matching the units of `translationVector`. For another camera pair, also pass its Triton intrinsics to the driver with `intrinsics_file`. The [camera kit source record](https://github.com/JeonHaneul/RL-based-Shelf-Sweeping-Camera-Kit/blob/main/SOURCE.md) identifies the distributed revision and the earlier submodule pin.

With the camera running, use `ros2 topic hz /triton/image_raw` and `ros2 topic hz /helios/pointcloud_rgb` to confirm both streams before starting detection. The [deployment README](../README.md#files-and-settings-to-provide) shows the workspace and calibration settings.
