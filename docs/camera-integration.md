# Camera integration

The camera repository will be integrated separately. The original project referenced `Holiclife-KTH/ROS2_Helios2_RGB_KIT` at `11ce7938a7a1947c7211066186f1d75b37c3607c`. That submodule is not presented as bundled or runnable in this distribution.

| Interface | Type | Default |
| --- | --- | --- |
| RGB input | `sensor_msgs/Image`, decoded as BGR8 | `/triton/image_raw`, overridden with `SWEEP_RGB_TOPIC` |
| Point-cloud input | `sensor_msgs/PointCloud2` | `/helios/pointcloud_rgb`, overridden with `SWEEP_POINTCLOUD_TOPIC` |
| Detected boxes | `custom_msgs/BBoxMultiArray` | `/segmentation/bboxes` |
| Target position | `geometry_msgs/PoseStamped` | `/pose_estimate/position` |
| Target width | `std_msgs/Float32` | `/pose_estimate/width` |

`pose_estimate.py` expects an OpenCV calibration file containing `cameraMatrix`, `distCoeffs`, `rotationVector`, and `translationVector`. Point-cloud coordinates, projection units, image resolution, distortion model, and frame names must agree with that calibration.

The recorded transform chain is `base_link -> opti_world -> triton_camera -> helios_camera`. The TCP is attached to `tool0_controller`. The numbers in `config/static_tf.json` are preserved experiment values, not calibration results for a new robot or camera position. Replace that file or set `SWEEP_TF_CONFIG` after calibration.

The original camera executable is `ros2 run lucid_camera_node lucid_node`. Its Arena SDK, camera network configuration, calibration files, and compatible source revision will be checked when the separate camera repository is supplied.
