from re import I
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from matplotlib.pyplot import tick_params
import numpy as np
import matplotlib.cm
import math
import os
import sys
import time

from pyqtgraph.colormap import ColorMap

wrapper_lib_path = os.getenv("CYBER_WRAPPER_LIB_PATH")
# print("wrapper_lib_path: {}".format(wrapper_lib_path))
if not wrapper_lib_path:
    wrapper_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../python_wrapper"))
# print("wrapper_lib_path: {}".format(wrapper_lib_path))
sys.path.append(wrapper_lib_path)

python_proto_path = os.getenv("PY_PROTO_PATH")
if not python_proto_path:
    python_proto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../python_wrapper"))
# print('python_proto_path: {}'.format(python_proto_path))
sys.path.append(python_proto_path)


from google.protobuf.descriptor import FileDescriptor
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf.text_format import MessageToString
import google.protobuf.text_format as text_format
import argparse

import car_state_pb2
import car_info_pb2
import control_command_pb2
import path_pb2
import planner_debug_pb2
import perception_object_pb2
import cyber


class RecordNode(QThread):
    emit_plot_signal = pyqtSignal(dict)
    planning_signal = pyqtSignal(dict)
    control_signal = pyqtSignal(dict)
    signal_length_signal = pyqtSignal(int)
    frame_history_signal = pyqtSignal(dict)
    behaviordebug_signal = pyqtSignal(list)
    reset_signal_list = pyqtSignal(list)
    front_to_vrp = 3.9624  # ego vehicle front to vrp distance
    wheel_base = 2.82
    steer_ratio = 16.8
    signal_length_max = 70

    def __init__(self):
        global name_csv
        QThread.__init__(self)
        cyber.init()
        self.file_path = "/opt/nio/json/online"
        # self.file_name=self.file_path+"/"+'online-%s.json'%currentTime
        self.file_name = ""
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.node = cyber.Node("listener")
        self.node.create_reader("/canbus/car_state", car_state_pb2.CarState, self.callback_car_state)
        self.node.create_reader("/planner/debug_info", planner_debug_pb2.PlannerDebug, self.callback_debug_info)
        self.node.create_reader("/control/control_command", control_command_pb2.ControlCommand, self.callback_control_command)
        self.node.create_reader("/canbus/car_info", car_info_pb2.CarInfo, self.callback_car_info)
        self.node.create_reader("/perception/predicted_objects", perception_object_pb2.PerceptionObjects, self.callback_predicted_objects)
        self.node.create_reader("/planner/path", path_pb2.Path, self.callback_path)
        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect()
        self.obs_id = 0
        self.update_visualizer = True
        self.signal_length = 0
        self.frame_id = self.signal_length - 1
        self.init_signal()
        self.init_writer()

    def emit_visualizer_frame(self):
        print("update visualizer frame id", self.frame_id, " visualizer frame length", len(self.visulizer_frame_history))
        frame = self.visulizer_frame_history[self.frame_id]
        for key in self.visulizer_frame:
            str = "self." + key + '_writer.write(frame["' + key + '"])'
            print("key  emit  ", str)
            exec(str)

        # self.car_state_writer.write(frame["car_state"])
        # self.path_writer.write(frame["path"])
        # self.predicted_objects_writer.write(frame["predicted_objects"])
        # self.car_info_writer.write(frame["car_info"])
        # self.debug_info_writer.write(frame["debug_info"])
        # self.control_command_writer.write(frame["control_command"])

    def init_writer(self):
        self.car_state_writer = self.node.create_writer("/canbus/car_state", car_state_pb2.CarState, qos_depth=1)
        self.debug_info_writer = self.node.create_writer("/planner/debug_info", planner_debug_pb2.PlannerDebug, qos_depth=1)
        self.control_command_writer = self.node.create_writer("/control/control_command", control_command_pb2.ControlCommand, qos_depth=1)
        self.car_info_writer = self.node.create_writer("/canbus/car_info", car_info_pb2.CarInfo, qos_depth=1)
        self.predicted_objects_writer = self.node.create_writer("/perception/predicted_objects", perception_object_pb2.PerceptionObjects, qos_depth=1)
        self.path_writer = self.node.create_writer("/planner/path", path_pb2.Path, qos_depth=1)

    def init_signal(self):
        self.reset = {"flag": True, "time_init": 0.0, "pos_init": []}
        self.signal = {
            "time": 0.0,
            "frame_id": 0.0,
            "ego_s": 0.0,
            "ego_speed": 0.0,
            "ego_lat_acc": 0.0,
            "ego_lon_acc": 0.0,
            "stop_state": 0.0,
            "path_fall_back": 0.0,
            "speed_fall_back": 0.0,
            "obs_s": 0.0,
            "obs_speed": 0.0,
            "obs_acc": 0.0,
            "obs_ds_dt": 0.0,
            "obs_dv_dt": 0.0,
            "obs_pos": [0.0, 0.0, 0.0],
            "steer_angle_speed_refer": 0.0,
            "steer_angle_refer": 0.0,
            "steer_angle_actual": 0.0,
            "steer_angle_cmd": 0.0,
            "steer_angle_speed_actual": 0.0,
            "lat_acc_refer": 0.0,
            "lat_jerk_refer": 0.0,
            "heding_refer": 0.0,
            "heading_actual": 0.0,
            "torque": 0.0,
            "dx_dt": 0.0,
            "dy_dt": 0.0,
            "pos_x": 0.0,
            "pos_y": 0.0,
            "speed_x": 0.0,
            "speed_y": 0.0,
            "refer_ds_dt": 0.0,
        }
        self.control_data_list = ["front_wheel_angle_rate", "angle", "acceleration", "turn_signal", "driving_mode"]
        self.control_simple_debug_data_list = [
            "lateral_error",
            "ref_heading",
            "heading",
            "heading_error",
            "heading_error_rate",
            "lateral_error_rate",
            "curvature",
            "steer_angle",
            "steer_angle_feedforward",
            "steer_angle_lateral_contribution",
            "steer_angle_lateral_rate_contribution",
            "steer_angle_heading_contribution",
            "steer_angle_heading_rate_contribution",
            "steer_angle_feedback",
            "steering_position",
            "steer_angle_limited",
            "speed_reference",
            "speed_error",
            "acceleration_reference",
            "speed",
            "acceleration_feedback",
            "acceleration_error",
            "lon_position_feedback",
            "cur_lon_position_reference",
            "cur_lon_position_error",
            "pre_lon_position_error",
            "pre_speed_error",
            "speed_cmd_limit",
            "pre_speed_reference",
            "pre_acceleration_reference",
            "pre_lon_position_reference",
            "lon_speed_feedforward",
            "pre_acceleration_error",
            "ref_pos_x",
            "ref_pos_y",
            "raw_curvature",
            "raw_lateral_error",
            "raw_lateral_error_rate",
            "raw_heading_error",
            "raw_heading_error_rate",
        ]
        for item in self.control_data_list:
            self.signal[item] = 0.0
        for item in self.control_simple_debug_data_list:
            self.signal[item] = 0.0
        self.SignalHistory = {}
        for key in self.signal.keys():
            self.SignalHistory[key] = []

        self.FrameResult = {}
        self.FrameResultHistory = []
        self.visulizer_frame = {}
        self.visulizer_frame_history = []

    def reset_obs(self, data):
        self.obs_id = data

    def reset_frame_id(self, data):
        self.frame_id = data + self.signal_length
        print("reset  frame id:", self.frame_id)
        self.emit_signal()
        self.emit_visualizer_frame()

    def callback_path(self, data):
        print("callback_path")
        if not self.update_visualizer:
            print("update visualizer path")
            return
        self.visulizer_frame["path"] = data
        self.signal["stop_state"] = data.stop_state
        self.FrameResult["steer_angle_speed_path"] = []
        self.FrameResult["steer_angle_path"] = []
        self.FrameResult["heading_path"] = []
        self.FrameResult["speed_path"] = []
        self.FrameResult["acc_lon_path"] = []
        self.FrameResult["acc_lat_path"] = []
        self.FrameResult["jerk_lat_path"] = []
        self.FrameResult["pos_s_path"] = []
        self.FrameResult["path_t"] = []
        self.FrameResult["pos_l_path"] = []
        self.FrameResult["kappa_path"] = []
        self.FrameResult["dkappa_path"] = []
        self.FrameResult["theta_path"] = []
        self.FrameResult["theta_path"] = []
        self.FrameResult["theta_path"] = []
        self.FrameResult["pos_dl_path"] = []
        self.FrameResult["pos_ddl_path"] = []
        t_init = (data.time_meas - self.reset["time_init"]) / 1000000000
        for pt in data.path_points:
            if pt.t < 0:
                continue
            kappa = pt.k
            dkappa = pt.dkappa
            speed = pt.speed
            val = dkappa / ((self.wheel_base * kappa) ** 2 + 1)
            self.FrameResult["jerk_lat_path"].append(2 * pt.acceleration * speed * pt.k + speed**3 * dkappa)
            front_angle = math.atan(kappa * self.wheel_base) * 180 / math.pi
            self.FrameResult["steer_angle_path"].append(front_angle * self.steer_ratio)
            front_angle_speed = val * speed * self.wheel_base * 180 / math.pi
            self.FrameResult["steer_angle_speed_path"].append(front_angle_speed * self.steer_ratio)
            self.FrameResult["heading_path"].append(pt.theta)
            self.FrameResult["speed_path"].append(speed)
            self.FrameResult["acc_lon_path"].append(pt.acceleration)
            self.FrameResult["acc_lat_path"].append(pt.speed**2 * pt.k)
            self.FrameResult["pos_s_path"].append(pt.s)
            self.FrameResult["path_t"].append(pt.t + t_init)
            self.FrameResult["pos_l_path"].append(pt.l)
            self.FrameResult["kappa_path"].append(pt.k)
            self.FrameResult["dkappa_path"].append(pt.dkappa)
            self.FrameResult["theta_path"].append(pt.theta)
            self.FrameResult["pos_dl_path"].append(pt.dl)
            self.FrameResult["pos_ddl_path"].append(pt.ddl)

        for item in self.FrameResult["path_t"]:
            if item < 0.2:
                continue
            self.signal["steer_angle_speed_refer"] = self.FrameResult["steer_angle_speed_path"][0]
            self.signal["steer_angle_refer"] = self.FrameResult["steer_angle_path"][0]
            self.signal["lat_acc_refer"] = data.path_points[0].k * data.path_points[0].speed ** 2
            # self.signal["lat_jerk_refer"] = jerk_lat_list[0]
            self.signal["heding_refer"] = data.path_points[0].theta
            break

        self.record_data()
        self.emit_signal()
        print("callback_path finished")

    def callback_car_info(self, data):
        print("callback_car_info ")
        if not self.update_visualizer:
            return
        self.visulizer_frame["car_info"] = data
        self.signal["steer_angle_actual"] = data.steer_report.actual_angle * 180 / math.pi
        self.signal["steer_angle_speed_actual"] = data.steer_report.wheel_speed * 180 / math.pi
        self.signal["torque"] = data.steer_report.torque
        print("callback_car_info finished")

    def callback_car_state(self, data):
        print("callback_car_state ")        
        time = (data.time_meas - self.reset["time_init"]) / 1000000000
        # print("car state call back , now", time, "  last", self.signal["time"])
        if len(self.SignalHistory["time"]) > 0 and time < self.signal["time"] and time >= self.SignalHistory["time"][0]:
            self.update_visualizer = False
            return
        self.update_visualizer = True

        # #print(" car_state call back,  time ",time)
        # if ((time - self.signal["time"]) < -0.01 or (time - self.signal["time"]) > 0.5):
        #     print(" car_state call back reset, now", time, "  last", self.signal["time"])
        #     self.reset["flag"] = True

        if self.reset["flag"]:
            self.init_signal()
            self.reset["time_init"] = data.time_meas
            self.reset["pos_init"] = [data.position.x, data.position.y, data.roll_pitch_yaw.z]

        self.visulizer_frame["car_state"] = data
        self.signal["time"] = time
        self.signal["ego_speed"] = data.speed
        self.signal["heading_actual"] = data.roll_pitch_yaw.z
        self.signal["ego_lat_acc"] = data.lateral_acceleration
        self.signal["ego_lon_acc"] = data.longitudinal_acceleration
        self.signal["ego_s"] = math.sqrt((self.reset["pos_init"][0] - data.position.x) ** 2 + (self.reset["pos_init"][1] - data.position.y) ** 2) + self.front_to_vrp
        self.signal["pos_x"] = data.position.x
        self.signal["pos_y"] = data.position.y
        self.signal["speed_x"] = data.velocity_enu.x
        self.signal["speed_y"] = data.velocity_enu.y

        num = len(self.SignalHistory["time"])
        if num > 1 and self.SignalHistory["time"][num - 1] > self.SignalHistory["time"][num - 2]:
            self.signal["dx_dt"] = (self.SignalHistory["pos_x"][num - 1] - self.SignalHistory["pos_x"][num - 2]) / (self.SignalHistory["time"][num - 1] - self.SignalHistory["time"][num - 2])
            self.signal["dy_dt"] = (self.SignalHistory["pos_y"][num - 1] - self.SignalHistory["pos_y"][num - 2]) / (self.SignalHistory["time"][num - 1] - self.SignalHistory["time"][num - 2])
        else:
            self.signal["dx_dt"] = 0.0
        print("callback_car_state finished")        
        
    def callback_control_command(self, data):
        print("callback_control_command")        
        if not self.update_visualizer:
            return
        self.visulizer_frame["control_command"] = data
        for item in self.control_data_list:
            str = 'self.signal["' + item + '"]=data.' + item
            exec(str)
        for item in self.control_simple_debug_data_list:
            str = 'self.signal["' + item + '"]=data.simple_debug.' + item
            exec(str)
        self.signal["steer_angle_cmd"] = self.signal["angle"] * 180 / math.pi * self.steer_ratio
        print("callback_control_command finished")        

    def project_x(self, item, heading):
        # return math.sqrt(item.x**2 + item.y**2)
        return item.x * math.cos(heading) + item.y * math.sin(heading)

    def calc_distance(self, item, pos):
        return math.sqrt((pos[0] - item[0]) ** 2 + (pos[1] - item[1]) ** 2)

    def clear_obs_info(self):
        self.signal["obs_speed"] = 0.0
        self.signal["obs_acc"] = 0.0
        self.signal["obs_pos"] = [0.0, 0.0, 0.0]
        self.signal["obs_s"] = 0.0
        self.clear_obs_perdiction_info()

    def clear_obs_perdiction_info(self):
        self.FrameResult["obs_perdiction_speed"] = []
        self.FrameResult["obs_perdiction_pos"] = []
        self.FrameResult["obs_perdiction_time"] = []

    def callback_predicted_objects(self, data):
        if not self.update_visualizer:
            return

        self.visulizer_frame["predicted_objects"] = data
        self.clear_obs_info()
        for item in data.objects:
            # print("obs id ", item.id)
            if item.id != self.obs_id:
                continue
            else:
                # print("obs id ", item.id)
                self.signal["obs_speed"] = self.project_x(item.velocity, self.reset["pos_init"][2])
                self.signal["obs_acc"] = self.project_x(item.acceleration, self.reset["pos_init"][2])
                self.signal["obs_pos"] = [item.position.x, item.position.y, item.heading]
                self.signal["obs_s"] = self.calc_distance(self.signal["obs_pos"], self.reset["pos_init"]) - item.bounding_box.x / 2.0
                if len(item.prediction) > 0 and len(item.prediction[0].trajectory) > 0:
                    self.FrameResult["obs_perdiction_speed"] = [waypoint.speed for waypoint in item.prediction[0].trajectory]
                    # print("obs prediction length ", len(self.FrameResult["obs_perdiction_speed"]))
                    self.FrameResult["obs_perdiction_pos"] = [
                        self.calc_distance([waypoint.position.x, waypoint.position.y, waypoint.heading], self.reset["pos_init"]) - item.bounding_box.x / 2.0
                        for waypoint in item.prediction[0].trajectory
                    ]
                    self.FrameResult["obs_perdiction_time"] = [(waypoint.time_delta) / 1000000000 + self.signal["time"] for waypoint in item.prediction[0].trajectory]

    def callback_debug_info(self, data):
        if not self.update_visualizer:
            return
        self.visulizer_frame["debug_info"] = data
        SLR = {}
        SLR["s"] = [item for item in data.motion_debug.path_boundary.x]
        for item in data.motion_debug.path_boundary.bound_lines:
            SLR[item.name] = [[it, [1, -1][it < 0] * 10][abs(it) > 10] for it in item.value]

        STR = {}
        if len(data.motion_debug.path_data_debug.path_points) > 0:
            init_s = data.motion_debug.path_data_debug.path_points[0].s
        else:
            init_s = 0.0
        STR["t"] = [item + self.signal["time"] for item in data.motion_debug.speed_boundary.x]
        for item in data.motion_debug.speed_boundary.bound_lines:
            STR[item.name] = [it + init_s for it in item.value]
        PathPoint = [[pb.s, pb.l, pb.theta, pb.k] for pb in data.motion_debug.path_data_debug.path_points]
        # print("path length=",len(PathPoint))
        SpeedPoint = [[pb.t + self.signal["time"], pb.s + init_s, pb.v, pb.a] for pb in data.motion_debug.speed_data_debug.speed_points]
        # print("speed length=",len(SpeedPoint))
        BehaviorPoint = [[pb.s, pb.k, pb.theta, pb.t + self.signal["time"], pb.l, pb.speed, pb.acceleration] for pb in data.behavior_result.ego_trajectory.path_points]
        BehaviorDebug = [[pb.seq_id, pb.action, pb.efficiency_cost, pb.safety_cost, pb.navigation_cost, pb.utility_cost, pb.final_cost] for pb in data.behavior_debug.action_sequence_info]
        SLTMapCube_data = [[pb.low_bnd_pt.s, pb.up_bnd_pt.s, pb.low_bnd_pt.l, pb.up_bnd_pt.l, pb.low_bnd_pt.t, pb.up_bnd_pt.t] for pb in data.motion_debug.slt_map.slt_map_cubes]
        for item in data.motion_debug.obs_decision_debug.decisions:
            # print("obs item t",item.t)
            # self.FrameResult["obs_decision_t"].append(item.t)
            for obs_decision in item.obs_decision:
                # print("obs item id",obs_decision.id,"obs item",obs_decision.decision)
                if obs_decision.id != self.obs_id:
                    continue
                self.FrameResult["obs_decision"].append(obs_decision.decision)
                break

        if len(SLTMapCube_data) > 0:
            time_pos = np.array([item[4] for item in SLTMapCube_data])
            colormap = matplotlib.cm.viridis
            positions = np.linspace(min(time_pos), max(time_pos), len(colormap.colors), endpoint=True)
            q_colormap = ColorMap(pos=positions, color=colormap.colors)
            color_for_points = q_colormap.map(time_pos)

        Cube = []
        for i, item in enumerate(SLTMapCube_data):
            s = [item[0], item[0], item[1], item[1], item[0]]
            s1 = [item[0], item[1], item[1], item[0], item[0]]
            l = [item[2], item[2], item[3], item[3], item[2]]
            t = [item[4], item[5], item[5], item[4], item[4]]
            c = color_for_points[i]
            Cube.append([s, l, t, s1, c])

        # self.signal["frame_id"] = data.frame_id
        self.signal["path_fall_back"] = data.motion_debug.fall_back_msg.path_fall_back_type
        self.signal["speed_fall_back"] = data.motion_debug.fall_back_msg.speed_fall_back_type

        self.FrameResult["SLR"] = SLR
        self.FrameResult["STR"] = STR
        self.FrameResult["SpeedPoint"] = SpeedPoint
        self.FrameResult["PathPoint"] = PathPoint
        self.FrameResult["BehaviorPoint"] = BehaviorPoint
        self.FrameResult["Cube"] = Cube
        self.FrameResult["behavior"] = BehaviorDebug

    def record_data(self):
        num = len(self.SignalHistory["time"])
        print("signal history length ", num)
        if num > 1 and self.SignalHistory["time"][num - 1] > self.SignalHistory["time"][num - 2]:
            self.signal["obs_ds_dt"] = self.calc_distance(self.SignalHistory["obs_pos"][num - 1], self.SignalHistory["obs_pos"][num - 2]) / (
                self.SignalHistory["time"][num - 1] - self.SignalHistory["time"][num - 2]
            )
            self.signal["obs_dv_dt"] = (self.SignalHistory["obs_speed"][num - 1] - self.SignalHistory["obs_speed"][num - 2]) / (
                self.SignalHistory["time"][num - 1] - self.SignalHistory["time"][num - 2]
            )

            item = [self.SignalHistory["ref_pos_x"][num - 1], self.SignalHistory["ref_pos_y"][num - 1]]
            item_2 = [self.SignalHistory["ref_pos_x"][num - 2], self.SignalHistory["ref_pos_y"][num - 2]]
            # print("refer ds dt calc")
            self.signal["refer_ds_dt"] = self.calc_distance(item, item_2) / (self.SignalHistory["time"][num - 1] - self.SignalHistory["time"][num - 2])

        for item in self.signal.keys():
            self.SignalHistory[item].append(self.signal[item])

        frame = {}
        for key in self.FrameResult.keys():
            frame[key] = self.FrameResult[key]
        self.FrameResultHistory.append(frame)

        frame = {}
        for key in self.visulizer_frame.keys():
            frame[key] = self.visulizer_frame[key]
        self.visulizer_frame_history.append(frame)

        if num > self.signal_length_max:
            self.visulizer_frame_history.pop(0)
            self.FrameResultHistory.pop(0)
            for key in self.SignalHistory:
                # print(key," history length ",len(self.SignalHistory[key]))
                self.SignalHistory[key].pop(0)

    def emit_signal(self):
        self.signal_length = len(self.FrameResultHistory)
        print("frame id:", self.frame_id, " frame_length", self.signal_length, "signal_length", len(self.SignalHistory["time"]), "key in ", "pos_s_path" in self.FrameResult)
        if self.signal_length > 0:
            if self.frame_id >= self.signal_length:
                self.frame_id = self.signal_length - 1
                print("modify frame id to :", self.frame_id)
                self.signal_length_signal.emit(self.signal_length)

            if self.signal_length < self.signal_length_max:
                self.signal_length_signal.emit(self.signal_length)

            self.control_signal.emit(self.SignalHistory)
            frame = self.FrameResultHistory[self.frame_id]
            self.planning_signal.emit(frame)
            if "behavior" in self.FrameResult:
                self.behaviordebug_signal.emit(frame["behavior"])
            self.frame_history_signal.emit(frame)

            plot_signal = {}
            for item in self.SignalHistory:
                plot_signal[item] = self.SignalHistory[item]
            for item in frame:
                plot_signal[item] = frame[item]
            # print("plot signal keys is:",plot_signal.keys())
            self.emit_plot_signal.emit(plot_signal)
            if self.reset["flag"]:
                self.reset_signal_list.emit(list(plot_signal.keys()))
            self.reset["flag"] = False

if __name__=="__main__":
    app = QApplication([])
    thread = RecordNode()
    thread.start()
    app.exec_()