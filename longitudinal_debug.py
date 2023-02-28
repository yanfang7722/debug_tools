#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PyQt5.QtWidgets import *
from pyqtgraph.functions import mkPen

color = ['y',  'b',  'g', 'm', [139, 105, 20], 'r', [
    255, 165, 0], [0, 255, 255], [255, 165, 0], [0, 191, 255]]


class LongDebug(QWidget):
    obs_id_signal = pyqtSignal(int)
    ds_dt = False
    perdiction = False
    planing = False
    data = {}

    def __init__(self):
        super(LongDebug, self).__init__()
        self.ObsEditID = QLineEdit(self)
        self.ObsEditID.setText(" 0 ")
        self.ObsEditID.editingFinished.connect(self.editFinish)
        self.obs_plot = self.ObsEditID.text =="0"
        self.DsDtPlot = QCheckBox("ds_dt")
        self.DsDtPlot.stateChanged.connect(
            lambda: self.btnstate(self.DsDtPlot))
        self.Perdiction = QCheckBox("perdiction")
        self.Perdiction.stateChanged.connect(
            lambda: self.btnstate(self.Perdiction))
        self.Planning = QCheckBox("planning")
        self.Planning.stateChanged.connect(
            lambda: self.btnstate(self.Planning))
        plot_control_layout = QHBoxLayout()
        plot_control_layout.addWidget(QLabel("obs id"))
        plot_control_layout.addWidget(self.ObsEditID)
        plot_control_layout.addWidget(self.DsDtPlot)
        plot_control_layout.addWidget(self.Perdiction)
        plot_control_layout.addWidget(self.Planning)
        self.plot_control = QWidget()
        self.plot_control.setLayout(plot_control_layout)

        self.graph = GraphicsLayoutWidget()
        self.graph_set()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.graph)
        self.main_layout.addWidget(self.plot_control)

    def editFinish(self):
        self.obs_id_signal.emit(int(self.ObsEditID.text()))
        self.obs_plot = ( self.ObsEditID.text  !="0")
        print("edit finish obs", int(self.ObsEditID.text()),"obs_plot",self.obs_plot)

    def btnstate(self, btn):
        str_exec = "self." + btn.text()+" = "+str(btn.isChecked())
        print(str_exec)
        exec(str_exec)

    def graph_set(self):
        # self.graph.setBackground('w')
        self.widget_s_cmp = self.graph.addPlot(0, 0)
        self.widget_s_cmp.setTitle("pos_s")
        self.widget_s_cmp.setLabel("left", "position(m)")
        self.widget_s_cmp.setLabel("bottom", "time [s]")
        self.widget_s_cmp.addLegend((150, 5))
        self.widget_s_cmp.showGrid(True, True)

        self.widget_speed = self.graph.addPlot(0, 1)
        self.widget_speed.setTitle("speed")
        self.widget_speed.setLabel("left", "m/s")
        self.widget_speed.setLabel("bottom", "time [s]")
        self.widget_speed.showGrid(True, True)
        # self.widget_speed.setXLink(self.widget_s_cmp)
        self.widget_speed.addLegend((150, 5))

        self.widget_acc = self.graph.addPlot(1, 1)
        self.widget_acc.setTitle("acc")
        self.widget_acc.setLabel("left", "m/s^2")
        self.widget_acc.setLabel("bottom", "time [s]")
        self.widget_acc.showGrid(True, True)
        self.widget_acc.addLegend((150, 5))

        self.widget_signal = self.graph.addPlot(1, 0)
        self.widget_signal.setTitle("driving mode")
        self.widget_signal.setLabel("bottom", "time [s]")
        self.widget_signal.showGrid(True, True)
        # self.widget_signal.setXLink(self.widget_speed)
        self.widget_signal.addLegend((150, 5))

        self.speed_cmd = self.widget_speed.plot(name="speed_cmd")
        self.speed_refer = self.widget_speed.plot(name="speed_reference")
        self.ego_speed = self.widget_speed.plot(name="ego_speed")
        self.obs_speed = self.widget_speed.plot(name="obs_speed")
        self.speed_planning = self.widget_speed.plot(name="speed_planning")

        self.acc_planning = self.widget_acc.plot(name="acc_lon_planning")
        self.acc_cmd = self.widget_acc.plot(name="acc_cmd")
        self.acc_refer = self.widget_acc.plot(name="acc_lon_refer")
        self.ego_lon_acc = self.widget_acc.plot(name="ego_lon_acc")
        self.lat_acc_refer = self.widget_acc.plot(name="lat_acc_refer")
        self.ego_lat_acc = self.widget_acc.plot(name="ego_lat_acc")
        self.obs_acc = self.widget_acc.plot(name="obs_acc")
        self.jerk_lat_planning = self.widget_acc.plot(name="lat_jerk")

        self.ego_s = self.widget_s_cmp.plot(name="ego_s")
        self.obs_s = self.widget_s_cmp.plot(name="obs_s")
        self.planing_s = self.widget_s_cmp.plot(name="planing_s")
        self.obs_perdict_s = self.widget_s_cmp.plot(name="obs_perdict_s")

        self.drive_mode = self.widget_signal.plot(name="drive_mode")
        self.stop_state = self.widget_signal.plot(name="stop_state")
        self.speed_fall_back = self.widget_signal.plot(name="speed_fall_back")
        self.path_fall_back = self.widget_signal.plot(name="path_fall_back")
        self.torque = self.widget_signal.plot(name="torque")

        self.obs_perdict_speed = self.widget_speed.plot(
            name="obs_perdict_speed")
        self.obs_acc_infer = self.widget_acc.plot(name="obs_dv_dt")
        self.obs_speed_infer = self.widget_speed.plot(name="obs_ds_dt")

    def update_frame(self, frame):
        #frame = data[0]
        if(self.perdiction and ("obs_perdiction_time" in frame)):
            self.obs_perdict_s.setData(
                frame["obs_perdiction_time"], frame["obs_perdiction_pos"], pen=mkPen(color[5], width=2))
            self.obs_perdict_speed.setData(
                frame["obs_perdiction_time"], frame["obs_perdiction_speed"], pen=mkPen(color[5], width=2))
        else:
            self.obs_perdict_s.setData([], [], pen=mkPen(color[5], width=2))
            self.obs_perdict_speed.setData(
                [], [], pen=mkPen(color[5], width=2))

        if(self.planing and ("path_t" in frame)):
            self.acc_planning.setData(
                frame["path_t"], frame["acc_lon_planning"], pen=mkPen(color[7], width=2))
            self.jerk_lat_planning.setData(
                frame["path_t"], frame["jerk_lat_planning"], pen=mkPen(color[8], width=2))
            self.speed_planning.setData(
                frame["path_t"], frame["speed_planning"], pen=mkPen(color[8], width=2))
            self.ego_lat_acc.setData(
                frame["path_t"], frame["acc_lat_planning"], pen=mkPen(color[6], width=2))
            # self.planing_s.setData(frame["path_t"], frame["pos_s"], pen=mkPen(color[5], width=2))
        else:
            self.acc_planning.setData([], [], pen=mkPen(color[7], width=2))
            self.ego_lat_acc.setData([], [], pen=mkPen(color[6], width=2))
            self.jerk_lat_planning.setData(
                [], [], pen=mkPen(color[9], width=2))
            self.speed_planning.setData([], [], pen=mkPen(color[7], width=2))
            self.planing_s.setData([], [], pen=mkPen(color[7], width=2))
        self.update_signal_plot()
        self.widget_s_cmp.enableAutoRange('xy', True)
        self.widget_speed.enableAutoRange('xy', True)
        self.widget_acc.enableAutoRange('xy', True)
        self.widget_signal.enableAutoRange('xy', True)

    def update_plot(self, data):
        self.data = data

    def update_signal_plot(self):
        data = self.data
        t = data["time"]
        self.speed_cmd.setData(
            t, data["speed"], pen=mkPen(color[0], width=2))
        self.speed_refer.setData(
            t, data["speed_reference"], pen=mkPen(color[1], width=2))
        self.ego_speed.setData(
            t, data["ego_speed"], pen=mkPen(color[2], width=2))
        if(self.obs_plot):
            self.obs_speed.setData(
                t, data["obs_speed"], pen=mkPen(color[3], width=2))
            self.obs_acc.setData(
                t, data["obs_acc"], pen=mkPen(color[5], width=2))
            self.obs_s.setData(data["time"], data["obs_s"],
                pen=mkPen(color[3], width=2))
        else:
            self.obs_s.setData(
                [],[],pen=mkPen(color[3], width=2))
            self.obs_speed.setData(
                [], [], pen=mkPen(color[3], width=2))
            self.obs_acc.setData(
                [], [], pen=mkPen(color[5], width=2))

        self.acc_cmd.setData(
            t, data["acceleration"], pen=mkPen(color[0], width=2))
        self.acc_refer.setData(
            t, data["acceleration_reference"], pen=mkPen(color[1], width=2))
        self.ego_lon_acc.setData(
            t, data["ego_lon_acc"], pen=mkPen(color[2], width=2))
        self.lat_acc_refer.setData(
            t, data["lat_acc_refer"], pen=mkPen(color[3], width=2))
        self.ego_lat_acc.setData(
            t, data["ego_lat_acc"], pen=mkPen(color[4], width=2))

        # self.jerk_lat_planning.setData(
        #    t, data["lat_jerk_refer"], pen=mkPen(color[5], width=2))
        self.obs_speed_infer.setData(
            t, data["refer_ds_dt"], pen=mkPen(color[6], width=2))
        if(self.ds_dt):
            self.obs_speed_infer.setData(
                t, data["obs_ds_dt"], pen=mkPen(color[6], width=2))
            self.obs_acc_infer.setData(
                t, data["obs_dv_dt"], pen=mkPen(color[6], width=2))
        else:
            self.obs_speed_infer .setData([], [], pen=mkPen(color[6], width=2))
            self.obs_acc_infer .setData(
                [], [], pen=mkPen(color=color[6], width=2))

        self.ego_s.setData(data["time"], data["ego_s"],
                           pen=mkPen(color[2], width=2))

        self.drive_mode.setData(
            t, data["driving_mode"], pen=mkPen(color[0], width=2))
        self.stop_state.setData(
            t, data["stop_state"], pen=mkPen(color[1], width=2))
        self.speed_fall_back.setData(data["time"], data["speed_fall_back"], pen=mkPen(
            color[3], width=2))
        self.path_fall_back.setData(data["time"], data["path_fall_back"], pen=mkPen(
            color[4], width=2))
        self.torque.setData(data["time"], data["torque"],
                            pen=mkPen(color[5], width=2))


if __name__ == "__main__":
    app = QApplication([])
    m = LongDebug()
    m.show()
    app.exec_()
