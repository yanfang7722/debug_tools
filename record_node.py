# import google.protobuf.text_format as text_format
# from google.protobuf.descriptor_pb2 import FileDescriptorProto
# from google.protobuf.descriptor import FileDescriptor

from copy import deepcopy
import threading
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
import os
import sys
import logging
from attr import has
import numpy as np

wrapper_lib_path = os.getenv("CYBER_WRAPPER_LIB_PATH")
# print("wrapper_lib_path: {}".format(wrapper_lib_path))
if not wrapper_lib_path:
    wrapper_lib_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../python_wrapper"))
# print("wrapper_lib_path: {}".format(wrapper_lib_path))
sys.path.append(wrapper_lib_path)

# python_proto_path = '/opt/nio/x86_64/lib/python/proto'
python_proto_path = os.getenv("PY_PROTO_PATH")
if not python_proto_path:
    python_proto_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../python_wrapper"))
# print('python_proto_path: {}'.format(python_proto_path))
sys.path.append(python_proto_path)


import car_state_pb2
import car_info_pb2
import control_command_pb2
import path_pb2
import planner_debug_pb2
import perception_object_pb2
import cyber

logger = logging.getLogger()
fmt = logging.Formatter(
    "[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[%(funcName)s]-[Line:%(lineno)d]-[Msg:%(message)s]")
sh = logging.StreamHandler()
fh = logging.FileHandler("record_play.log")
sh.setFormatter(fmt)
fh.setFormatter(fmt)
logger.addHandler(sh)
logger.addHandler(fh)


class RecordNode(QThread):
    signal_length_max = 70
    main_topic = "path"
    # mode, -1:no var, 0:only signal var, 1:signal var and first level repeated,2:all
    # is required topic
    topic_dict = {
        "/canbus/car_state": [" car_state_pb2.CarState", 2, True],
        "/canbus/car_info": [" car_info_pb2.CarInfo", -1, True],
        "/control/control_command": [" control_command_pb2.ControlCommand", 0, True],
        "/planner/debug_info": [" planner_debug_pb2.PlannerDebug", -1, True],
        "/planner/debug_info_old": [" planner_debug_pb2.PlannerDebug", -1, False],
        "/perception/predicted_objects": ["perception_object_pb2.PerceptionObjects", -1, True],
        "/planner/path": [" path_pb2.Path", -1, False],
        "/planner/path_old": [" path_pb2.Path", -1, False],
    }

    plotted_signal_data_pyqt = pyqtSignal(dict)
    history_length_pyqt = pyqtSignal(int)
    all_signal_name_list_pyqt = pyqtSignal(list)

    def __init__(self):
        QThread.__init__(self)
        self.lock = threading.Lock()
        cyber.init()
        self.node = cyber.Node("listener")
        self.init_signal()
        self.init_plot_signal()
        for key, value in self.topic_dict.items():
            topic_name = key.split("/")[-1]
            create_reader = 'self.node.create_reader("' + key + '",' + \
                value[0] + ', self.call_back_creator("' + topic_name + '"))'
            exec(create_reader)
            create_writer = "self." + topic_name + \
                '_writer = self.node.create_writer("' + \
                key + '",' + value[0] + ", qos_depth=1)"
            exec(create_writer)
        self.read_record = True
        self.plot_signal_list = []

    def init_signal(self):
        self.signal_length = 0
        self.slider_value = -1
        self.frame_id = self.signal_length + self.slider_value
        self.var_name_reset_flag = {}
        self.sequence_signal_lists = {}
        self.frame_signal_dicts = {}
        for key, value in self.topic_dict.items():
            topic_name = key.split("/")[-1]
            self.var_name_reset_flag[topic_name] = True
        self.reset = {"flag": True, "time_init": 0.0,
                      "pos_init": [], "var_name_reset": True}
        self.delta_time = 0.0

        self.sequence_proto = {}
        self.sequence_post = {}
        self.sequence_history = {}

        self.frame_proto = {}
        self.frame_post = {}
        self.frame_history = []

        self.visulizer_frame = {}
        self.visulizer_frame_history = []

    def init_plot_signal(self):
        self.init_post_process_signal()
        for key, value in self.topic_dict.items():
            topic_name = key.split("/")[-1]
            self.sequence_signal_lists[topic_name] = set()
            self.frame_signal_dicts[topic_name] = {}
        self.sequence_signal_lists_all = deepcopy(self.sequence_signal_lists)
        self.frame_signal_dicts_all = deepcopy(self.frame_signal_dicts)

    def init_post_process_signal(self):
        # attention:post_processs_signal should end with "_post",both frame and

        # sequence_post
        self.sequence_post["steer_angle_post"] = 0.0
        self.sequence_post["path.time_meas_post"]=0.0

        # frame_post
        self.frame_post["path.jerk_lat[i]_post"] = []
        self.frame_post["path.acc_lat[i]_post"] = []
        self.frame_post["path.path_points[i].t_post"] = []
        self.frame_post["path.jerk[i]_post"] = []
        path_bound_str = "debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i]"
        self.frame_post[path_bound_str+".hard_bound.lb_post"] = []
        self.frame_post[path_bound_str+".hard_bound.ub_post"] = []
        self.frame_post[path_bound_str+".hard_bound.x_post"] = []
        self.frame_post[path_bound_str+".nudge_bound.ub_post"] = []
        self.frame_post[path_bound_str+".nudge_bound.x_post"] = []
        self.frame_post[path_bound_str+".cross_bound.ub_post"] = []
        self.frame_post[path_bound_str+".cross_bound.x_post"] = []
        self.frame_post[path_bound_str+".nudge_bound.lb_post"] = []
        self.frame_post[path_bound_str+".nudge_bound.x_post"] = []
        self.frame_post[path_bound_str+".cross_bound.lb_post"] = []
        self.frame_post[path_bound_str+".cross_bound.x_post"] = []
        speed_bound_str = "debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i]"
        self.frame_post[speed_bound_str+".hard_bound.lb_post"] = []
        self.frame_post[speed_bound_str+".hard_bound.ub_post"] = []
        self.frame_post[speed_bound_str+".hard_bound.x_post"] = []
        self.frame_post[speed_bound_str+".yield.ub_post"] = []
        self.frame_post[speed_bound_str+".yield.x_post"] = []
        self.frame_post[speed_bound_str+".align_yield.ub_post"] = []
        self.frame_post[speed_bound_str+".align_yield.x_post"] = []
        self.frame_post[speed_bound_str +".align_not_yield.lb_post"] = []
        self.frame_post[speed_bound_str +".align_not_yield.x_post"] = []

    def time_stamp_to_sec(self, ts):
        sec = (ts / 1e9 - self.reset["time_init"]
               ) + self.reset["time_init"] % 60
        return sec

    def sequence_signal_lists_assignment(self, topic_name, data):
        exec(topic_name + "=data")
        for item in self.sequence_signal_lists[topic_name]:
            self.sequence_proto[item] = 0.0
            attr_name_list = item.split(".")
            if len(attr_name_list) < 2:
                print(topic_name, "call back, ", item,
                      "attr name  length", attr_name_list)
                continue
            try:
                signal_value = eval(item)
            except:
                signal_value = 0.0
                # print("signal:",item," value error, use",0.0)
            self.signal[item] = signal_value

    def frame_signal_dicts_assignment(self, topic_name, data):
        exec(topic_name + "=data")
        for frame_name, frame_signal_list in self.frame_signal_dicts[topic_name].items():
            # print("frame_name:",frame_name,"frame_signal_list:",frame_signal_list)
            try:
                frame_name_data = eval(frame_name)
                if (not frame_name_data):
                    # print(frame_name,"data is empty")
                    continue
            except:
                # print("record call back, frame name error", "not a attr of", frame_name)
                continue
            for frame_signal in frame_signal_list:
                frame_signal_name = frame_name + "[i]" + frame_signal[4:]
                self.frame_proto[frame_signal_name] = []
                frame_signal_name_0 = frame_signal_name.replace(
                    "[i]", "[0]")
                try:
                    eval(frame_signal_name_0)
                except:
                    # print("record call back, frame_signal_name error", "not a attr of", frame_signal_name_0)
                    continue
                for i, item in enumerate(eval(frame_name)):
                    try:
                        signal_value = eval(frame_signal)
                    except:
                        signal_value = 0.0
                        # print("frame_signal:", frame_name, " ", frame_signal, " value error, use", 0.0)

                    # if ("time_meas" in frame_signal) or ("planning_timestamp" in frame_signal):
                    #     val = self.time_stamp_to_sec(signal_value)
                    # else:
                        # val = signal_value

                    val = signal_value
                    try:
                        self.frame_proto[frame_signal_name].append(val)
                    except KeyError:
                        # print("record call back,val:", val, " signal_name", frame_signal_name, " data", self.frame_proto.keys())
                        continue

    def call_back_creator(self, topic_name):
        def call_back_func(data):
            self.lock.acquire()
            print(topic_name, " call back start")
            exec(topic_name + "=data")
            if not self.read_record:  # replay mode
                attr_name = topic_name + ".time_meas"
                if hasattr(data, "time_meas") and attr_name in self.sequence_signal_lists[topic_name] and self.time_stamp_to_sec(data.time_meas) > self.sequence_proto[attr_name]:
                    self.read_record = True
                else:
                    print(
                        topic_name, " call back return for read_record is ", self.read_record)
                    if topic_name == self.main_topic:
                        self.emit_signal()
                    self.lock.release()
                    return
            self.visulizer_frame[topic_name] = data

            if self.reset["flag"]:  # record init time when first topic call back
                if hasattr(data, "time_meas"):
                    self.reset["flag"] = False
                    self.reset["time_init"] = getattr(data, "time_meas") / 1e9
                else:
                    self.lock.release()
                    return
            if hasattr(data, "time_meas"):
                self.sequence_proto[topic_name+".time_meas"]=self.time_stamp_to_sec(getattr(data, "time_meas"))

            if self.var_name_reset_flag[topic_name]:
                get_name(
                    topic_name, data, self.sequence_signal_lists_all[topic_name], self.frame_signal_dicts_all[topic_name])
                print(topic_name, self.sequence_signal_lists_all[topic_name])
                print("\n", topic_name,
                      self.frame_signal_dicts_all[topic_name])
                print()
                self.var_name_reset_flag[topic_name] = False

            self.sequence_signal_lists_assignment(topic_name, data)
            self.frame_signal_dicts_assignment(topic_name, data)

            self.frame_signal_post_process(topic_name, data)
            self.sequence_signal_post_process_and_record(topic_name, data)

            if topic_name == self.main_topic:
                frame=deepcopy(self.frame_proto)
                frame.update(self.frame_post)
                for item in frame:
                    print("main topic==",item,"size:",len(frame[item]))
                self.frame_history.append(frame)
                self.visulizer_frame_history.append(
                    deepcopy(self.visulizer_frame))
                if len(self.frame_history) > self.signal_length_max:
                    self.frame_history.pop(0)
                    self.visulizer_frame_history.pop(0)
                self.emit_signal()
                self.init_post_process_signal()
            # print(topic_name, " call back finished")
            self.lock.release()
            return
        return call_back_func

    def emit_visualizer_frame(self):
        frame_id = self.signal_length + self.slider_value
        print("update visualizer frame id", frame_id,
              " visualizer frame length", len(self.visulizer_frame_history))
        for key in self.visulizer_frame:
            topic_writer = "self." + key + \
                '_writer.write(frame["' + key + '"])'
            print("visualizer key  emit  ", topic_writer)
            exec(topic_writer)

    def frame_signal_post_process(self, topic_name, data):
        if "path" == topic_name:
            for index, pt in enumerate(data.path_points):
                self.frame_post["path.jerk_lat[i]_post"].append(
                    2 * pt.acceleration * pt.speed * pt.k + pt.speed**3 * pt.dkappa)
                self.frame_post["path.acc_lat[i]_post"].append(
                    pt.speed**2 * pt.k)
                self.frame_post["path.path_points[i].t_post"].append(
                    pt.t + self.sequence_proto["path.time_meas"])
                if index > 0:
                    self.frame_post["path.jerk[i]_post"].append(
                        (pt.acceleration - self.visulizer_frame["path"].path_points[index - 1].acceleration) / (
                            pt.t - self.visulizer_frame["path"].path_points[index - 1].t)
                    )
                else:
                    self.frame_post["path.jerk[i]_post"].append(0)
        elif "debug_info" == topic_name:
            data = data
            obs_ids = []
            path_bound_str = "debug_info.motion_debug.path_constraint_debug.bound_constraint_points[i]"
            for item in data.motion_debug.path_constraint_debug.bound_constraint_points:
                if (hasattr(item, "hard_bound")):
                    if (item.hard_bound.solution_distance_to_lb > 1e-3 and item.hard_bound.lb_obs_id):
                        obs_ids.append(item.hard_bound.lb_obs_id)
                    if (item.hard_bound.solution_distance_to_ub > 1e-3 and item.hard_bound.ub_obs_id):
                        obs_ids.append(item.hard_bound.ub_obs_id)
                    self.frame_post[path_bound_str+".hard_bound.lb_post"] .append(
                        item.hard_bound.lb)
                    self.frame_post[path_bound_str+".hard_bound.ub_post"] .append(
                        item.hard_bound.ub)
                    self.frame_post[path_bound_str+".hard_bound.x_post"] .append(
                        item.x)
                elif (hasattr(item, "upper_bound")):
                    for ub_item in item.upper_bound:
                        if (item.upper_bound.epsilon < 1e-3 and item.upper_bound.obs_id):
                            obs_ids.append(item.upper_bound.obs_id)
                        if (ub_item.bnd_source_type == "CROSSABLE_LANE"):
                            self.frame_post[path_bound_str+".cross_bound.ub_post"].append(
                                ub_item.bnd_position)
                            self.frame_post[path_bound_str+".cross_bound.x_post"].append(
                                item.x)
                        elif (ub_item.bnd_source_type == "NUDGE_OBS"):
                            self.frame_post[path_bound_str+".nudge_bound.x_post"].append(
                                ub_item.bnd_position)
                            self.frame_post[path_bound_str+".nudge_bound.ub_post"].append(
                                item.x)
                elif (hasattr(item, "lower_bound")):
                    for lb_item in item.lower_bound:
                        if (item.lower_bound.epsilon > -1e-3 and item.lower_bound.obs_id):
                            obs_ids.append(item.lower_bound.obs_id)
                        if (lb_item.bnd_source_type == "CROSSABLE_LANE"):
                            self.frame_post[path_bound_str+".cross_bound.lb_post"].append(
                                lb_item.bnd_position)
                            self.frame_post[path_bound_str+".cross_bound.x_post"].append(
                                item.x)
                        elif (lb_item.bnd_source_type == "NUDGE_OBS"):
                            self.frame_post[path_bound_str+".nudge_bound.lb_post"].append(
                                lb_item.bnd_position)
                            self.frame_post[path_bound_str+".nudge_bound.x_post"].append(
                                item.x)

            speed_bound_str = "debug_info.motion_debug.speed_constraint_debug.bound_constraint_points[i]"
            for item in data.motion_debug.speed_constraint_debug.bound_constraint_points:
                if (hasattr(item, "hard_bound")):
                    if (item.hard_bound.solution_distance_to_lb > 1e-3 and item.hard_bound.lb_obs_id):
                        obs_ids.append(item.hard_bound.lb_obs_id)
                    if (item.hard_bound.solution_distance_to_ub > 1e-3 and item.hard_bound.ub_obs_id):
                        obs_ids.append(item.hard_bound.ub_obs_id)
                    self.frame_post[speed_bound_str+".hard_bound.x_post"] .append(
                        item.x)
                    self.frame_post[speed_bound_str+".hard_bound.lb_post"] .append(
                        item.hard_bound.lb)
                    self.frame_post[speed_bound_str+".hard_bound.ub_post"] .append(
                        item.hard_bound.ub)
                elif (hasattr(item, "lower_bound")):
                    for ub_item in item.lower_bound:
                        if (item.lower_bound.epsilon < 1e-3 and item.lower_bound.obs_id):
                            obs_ids.append(
                                item.lower_bound.obs_id and item.lower_bound.obs_id)
                        if (ub_item.bnd_source_type == "ALIGN_NOT_YIELD"):
                            self.frame_post[speed_bound_str+".align_not_yield.x_post"].append(
                                item.x)
                            self.frame_post[speed_bound_str+".align_not_yield.lb_post"].append(
                                ub_item.bnd_position)
                elif (hasattr(item, "upper_bound")):
                    for ub_item in item.upper_bound:
                        if (item.upper_bound.epsilon < 1e-3 and item.upper_bound.obs_id):
                            obs_ids.append(item.upper_bound.obs_id)
                        if (ub_item.bnd_source_type == "YIELD" or ub_item.bnd_source_type == "SLOT_YIELD"):
                            self.frame_post[speed_bound_str+".yield.x_post"].append(
                                item.x)
                            self.frame_post[speed_bound_str+".yield.ub_post"].append(
                                ub_item.bnd_position)
                        elif (ub_item.bnd_source_type == "ALIGN_YIELD"):
                            self.frame_post[speed_bound_str+".align_yield.x_post"].append(
                                item.x)
                            self.frame_post[speed_bound_str+".align_yield.ub_post"].append(
                                ub_item.bnd_position)

    def sequence_signal_post_process_and_record(self, topic_name, data):
        # post
        if "debug_info " == topic_name:
            self.sequence_proto["debug_info.planning_timestamp"] = self.time_stamp_to_sec(
                data.planning_timestamp)
        elif hasattr(data, "time_meas"):
            self.sequence_proto[topic_name +
                                ".time_meas"] = self.time_stamp_to_sec(data.time_meas)
            self.delta_time = self.sequence_proto[topic_name +
                                                  ".time_meas"] - self.reset["time_init"]

        for item in self.sequence_signal_lists[topic_name]:
            if item not in self.sequence_history:
                print(item, " not in history, add pre list ")
                self.sequence_history[item] = []
            self.sequence_history[item].append(self.sequence_proto[item])
            if self.delta_time > 7:
                self.sequence_history[item].pop(0)
        for item in self.sequence_post:
            if item not in self.sequence_history:
                print(item, " not in history, add pre list ")
                self.sequence_history[item] = []
            self.sequence_history[item].append(self.sequence_post[item])
            if self.delta_time > 7:
                self.sequence_history[item].pop(0)                

    def emit_signal(self):
        self.signal_length = len(self.frame_history)
        frame_id = self.signal_length + self.slider_value
        if self.signal_length > 1:
            if frame_id >= self.signal_length:
                # print("frame id large:", frame_id, "  modify frame id to :", self.signal_length - 1)
                frame_id = self.signal_length - 1
                self.history_length_pyqt.emit(self.signal_length)

            if self.signal_length < self.signal_length_max:
                self.history_length_pyqt.emit(self.signal_length)
                # print("emit history length signal", self.signal_length)

            frame = self.frame_history[frame_id]
            if self.reset["var_name_reset"]:
                if np.array(list(self.var_name_reset_flag.values())).any() == 0 or self.signal_length > 5:
                    self.reset["var_name_reset"] = False
                else:
                    print("not all var name updated, waiting", self.var_name_reset_flag, "  ", np.array(
                        list(self.var_name_reset_flag.values())).any())
                    return
                new_signal_list = self.get_all_signal_list()
                self.all_signal_name_list_pyqt.emit(new_signal_list)

            plot_signal_data = {}
            for item in self.plot_signal_list:
                topic_name = item.split(".")[0]
                if item in self.sequence_history:
                    plot_signal_data[item] = self.sequence_history[item]
                elif item in frame:
                    plot_signal_data[item] = frame[item]
                else:
                    print("emit signal", item, "not exist")
            self.plotted_signal_data_pyqt.emit(plot_signal_data)
            # print("emit plotted signal data, plotted_signal_names:",plot_signal_data.keys())
            print("emit signal finished,frame id", self.frame_id)

    def update_plotted_signal_list(self, data):
        print("record update_emitted_signal_list", data)
        self.plot_signal_list = data
        print("=====begin===")
        self.get_var_from_plotted_signal(self.plot_signal_list)
        print("sequence_signal_lists==",self.sequence_signal_lists)
        print("frame_signal_dicts==",self.frame_signal_dicts)
        print("========")
        self.plot_signal_list.append("debug_info.BehaviorDebug")
        print("self.call_back_" + self.main_topic +
              "(self.visulizer_frame[" + self.main_topic + "])")
        self.emit_signal()

    def reset_frame_id(self, data):
        self.lock.acquire()
        self.slider_value = data
        print("reset  frame id:", self.slider_value)
        self.read_record = False
        frame_id = self.signal_length + self.slider_value
        self.frame_proto = self.frame_history[frame_id]
        self.emit_visualizer_frame()
        # self.emit_signal()
        self.lock.release()

    def reset_data(self, data):
        self.lock.acquire()
        print("record signal, reset data")
        self.init_signal()
        self.emit_signal()
        self.lock.release()

    def get_var_from_plotted_signal(self, var_list):
        self.init_plot_signal()
        for item in var_list:
            if ("_post" in item):
                continue  # filter post signal
            topic_name = item.split(".")[0]
            if ("[i]" in item):
                frame_signal = item.split("[i]")
                if (len(frame_signal) > 2):
                    print("item has too many [i]", item)
                    continue
                var_key = frame_signal[0]
                new_item = "item" + frame_signal[1]
                if var_key not in self.frame_signal_dicts[topic_name]:
                    self.frame_signal_dicts[topic_name][var_key] = []
                self.frame_signal_dicts[topic_name][var_key].append(new_item)
            else:
                self.sequence_signal_lists[topic_name].add(item)


    def get_all_signal_list(self):
        new_signal_list = []
        for topic_signal_list in self.sequence_signal_lists_all.values():
            for item in topic_signal_list:
                new_signal_list.append(item)
        for topic_frame_signal_list in self.frame_signal_dicts_all.values():
            for frame_name in topic_frame_signal_list:
                for frame_signal in topic_frame_signal_list[frame_name]:
                    frame_signal_name = frame_name + "[i]" + frame_signal[4:]
                    new_signal_list.append(frame_signal_name)
        for item in self.frame_post:
            new_signal_list.append(item)
        for item in self.sequence_post:
            new_signal_list.append(item)
        return new_signal_list

def get_name(str_name, obj, var_name_set, frame_name_dict, get_mode=2):
    debug_state = "obstacle_debug_maps" in str_name
    if get_mode < 0:
        return
    if not hasattr(obj, "DESCRIPTOR"):
        if not get_mode:
            print("get var name get_mode", get_mode, " str_name", str_name)
            return
        if debug_state:
            print(str_name, "obstacle_debug_maps,", type(obj))
        frame_name_list = set()
        for index, sub_obj in enumerate(obj):
            if debug_state:
                print(str_name, "obstacle_debug_maps,", type(sub_obj))

            if type(sub_obj) in (int, float, bool, bytes, str):
                frame_name_list.add("item")
            else:
                sub_frame_dict = {}
                get_name("item", sub_obj, frame_name_list,
                         sub_frame_dict, get_mode)
                if not sub_frame_dict:
                    if debug_state:
                        print("sub_dict is empty", sub_frame_dict)
                    break
                elif get_mode > 1:
                    if debug_state:
                        print("sub_dict", sub_frame_dict)
                    for key, value in sub_frame_dict.items():
                        var_name = str_name + "[" + str(index) + "]" + key[4:]
                        frame_name_dict[var_name] = value
                        if debug_state:
                            print(var_name, "value is : ", value)

        if frame_name_list:
            frame_name_dict[str_name] = frame_name_list
        else:
            if debug_state:
                print(str_name, "is empty, not added")
            return
        return

    for field_name in obj.DESCRIPTOR.fields:
        item = field_name.name
        if hasattr(obj, item):
            sub_obj = getattr(obj, item)
            # print( var_name," type is: ",type(a))
            var_name = str_name + "." + item
            if type(sub_obj) in (int, float, bool, bytes, str):
                # print( var_name," type is: ",type(a),"data is:",a,"add to list")
                var_name_set.add(var_name)
            else:
                # print( var_name,"need recursive type is: ",type(sub_obj))
                get_name(var_name, sub_obj, var_name_set,
                         frame_name_dict, get_mode)
                # print(var_name,"dir is:",dir(sub_obj))
        else:
            print(item, "get name not exist ====")


if __name__ == "__main__":
    app = QApplication([])
    thread = RecordNode()
    thread.start()
    data = ["car_state.time_meas", "control_command.simple_debug.speed_reference",
            "control_command.simple_debug.debug_path.path_points[i].ddl"]
    thread.update_plotted_signal_list(data)
    app.exec_()
