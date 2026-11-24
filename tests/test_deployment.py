"""Isolated checks. No ROS nodes, policy files, or robot connections are created."""
import ast
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


paths = load_file('deployment_paths', ROOT/'src/base_package/base_package/runtime_config.py')
solver = load_file('deployment_solver', ROOT/'src/control_package/control_package/POE_Robot_Kinematics_Solver/robot_kinematic_solver.py')


class PathTests(unittest.TestCase):
    def test_paths_do_not_depend_on_working_directory(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as temporary, patch.dict(os.environ, {}, clear=True):
            assert Path(temporary).resolve().is_relative_to(ROOT.resolve())
            try:
                os.chdir(temporary)
                self.assertEqual(paths.workspace_root(), ROOT)
                self.assertEqual(Path(paths.model_path()), ROOT/'models/vision/best.pt')
                self.assertTrue(Path(paths.resource_path('control_package','260311/params/env.yaml')).is_file())
            finally:
                os.chdir(previous)

    def test_relative_and_absolute_settings_and_log_creation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as temporary:
            assert Path(temporary).resolve().is_relative_to(ROOT.resolve())
            with patch.dict(os.environ, {'SWEEP_WORKSPACE':temporary,'SWEEP_POLICY_DIR':'policy','SWEEP_LOG_DIR':str(Path(temporary)/'output')}, clear=True):
                self.assertEqual(Path(paths.policy_directory()), Path(temporary)/'policy')
                log = Path(paths.log_path('drl/traj.csv'))
                self.assertEqual(log, Path(temporary)/'output/drl/traj.csv')
                self.assertTrue(log.parent.is_dir())

    def test_robot_address_must_be_explicit(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                paths.robot_ip()
        with patch.dict(os.environ, {'SWEEP_ROBOT_IP':'192.0.2.10'}, clear=True):
            self.assertEqual(paths.robot_ip(), '192.0.2.10')


class ObservationTests(unittest.TestCase):
    def setUp(self):
        path = ROOT/'src/control_package/control_package/DRL/ur.py'
        source = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(item for item in source.body if isinstance(item, ast.ClassDef) and item.name=='URSweepPolicy')
        namespace = {'np':np,'PolicyController':object}
        exec(compile(ast.Module(body=[cls],type_ignores=[]),str(path),'exec'),namespace)
        self.policy = namespace['URSweepPolicy'].__new__(namespace['URSweepPolicy'])
        self.policy.has_joint_data = True
        self.policy.has_tcp_data = True
        self.policy.current_joint_positions = np.arange(6,dtype=float)
        self.policy.default_pos = np.zeros(6)
        self.policy.current_joint_velocities = np.arange(6,dtype=float)/10
        self.policy._previous_action = np.arange(7,dtype=float)/10
        self.policy.target_pos = np.array([.6,.2,.3])
        self.policy.goal_pos = np.array([.6,.38,.3])
        self.policy._target_object_width = .05
        self.policy.current_tcp_pose = np.array([.5,.1,.3,1,0,0,0])

    def test_complete_observation_order(self):
        result = self.policy._compute_observation()
        self.assertEqual(result.shape,(1,35))
        self.assertEqual(result.dtype,np.float32)
        np.testing.assert_allclose(result[0,:6],np.arange(6))
        np.testing.assert_allclose(result[0,6:8],[.04,.04])
        np.testing.assert_allclose(result[0,14:21],self.policy._previous_action)
        np.testing.assert_allclose(result[0,21:24],self.policy.target_pos)
        self.assertAlmostEqual(float(result[0,24]),.05)
        np.testing.assert_allclose(result[0,25:32],self.policy.current_tcp_pose)
        np.testing.assert_allclose(result[0,32:35],self.policy.goal_pos)

    def test_partial_robot_state_does_not_produce_observation(self):
        for flag in ('has_joint_data','has_tcp_data'):
            with self.subTest(missing=flag):
                setattr(self.policy,flag,False)
                self.assertIsNone(self.policy._compute_observation())
                setattr(self.policy,flag,True)

    def test_missing_width_does_not_produce_observation(self):
        self.policy._target_object_width=None
        self.assertIsNone(self.policy._compute_observation())


class KinematicsTests(unittest.TestCase):
    def test_poe_matches_direct_dh_product(self):
        q=np.array([.2,-1.1,1.3,-1.2,.6,.3])
        expected=np.eye(4)
        for angle,(a,d,alpha) in zip(q,solver.UR5E_CONFIG.dh_params):
            c,s=np.cos(angle),np.sin(angle)
            ca,sa=np.cos(alpha),np.sin(alpha)
            expected=expected@np.array([[c,-s*ca,s*sa,a*c],[s,c*ca,-c*sa,a*s],[0,sa,ca,d],[0,0,0,1]])
        offset=np.eye(4)
        offset[:3,3]=solver.UR5E_CONFIG.tool_offset
        expected=expected@offset
        actual=solver.RobotKinematicsPOE(solver.UR5E_CONFIG).forward_kinematics(q)
        np.testing.assert_allclose(actual,expected,atol=1e-10)

    def test_ik_recovers_pose_from_nearby_seed(self):
        robot=solver.RobotKinematicsPOE(solver.UR5E_CONFIG)
        q=np.array([.2,-1.1,1.3,-1.2,.6,.3])
        target=robot.forward_kinematics(q)
        result=robot.inverse_kinematics(target,q+.02)
        self.assertTrue(result.converged)
        np.testing.assert_allclose(robot.forward_kinematics(result.joints),target,atol=2e-4)


if __name__=='__main__':
    unittest.main()
