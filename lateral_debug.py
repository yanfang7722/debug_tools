#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from os import name
from PyQt5.QtCore import *
from numpy.core.fromnumeric import shape
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PyQt5.QtWidgets import *
from pyqtgraph.functions import mkPen

color = ['y',  'b',  'g', 'm', [139, 105, 20], 'r',[255,165,0],[0,255,255],[255,165,0]]


class LateralDebug(QWidget):
    obs_id_signal = pyqtSignal(int)
    ds_dt = False
    perdiction = False
    planing = True

    def __init__(self):
        super(LateralDebug, self).__init__()
        self.ObsEditID = QLineEdit(self)
        self.ObsEditID.setText(" 0 ")
        self.ObsEditID.editingFinished.connect(self.editFinish)
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
        print("edit finish obs", int(self.ObsEditID.text()))

    def btnstate(self, btn):
        str_exec = "self." + btn.text()+" = "+str(btn.isChecked())
        print(str_exec)
        exec(str_exec)

    def graph_set(self):
        # self.graph.setBackground('w')
        self.widget_heading = self.graph.addPlot(0, 0)
        self.widget_heading.setTitle("heading (deg) ")
        self.widget_heading.setLabel("bottom", "time [s]")
        self.widget_heading.showGrid(True, True)
        self.widget_heading.addLegend((150, 5))

        self.widget_steer = self.graph.addPlot(1, 0)
        self.widget_steer.setTitle("streering angle (deg)")
        self.widget_steer.setLabel("bottom", "time [s]")
        self.widget_steer.showGrid(True, True)
        self.widget_steer.setXLink(self.widget_heading)
        self.widget_steer.addLegend((150, 5))

        self.widget_steer_speed = self.graph.addPlot(0, 1)
        self.widget_steer_speed.setTitle("streering angle speed (deg)")
        self.widget_steer_speed.setLabel("bottom", "time [s]")
        self.widget_steer_speed.showGrid(True, True)
        self.widget_steer_speed.setXLink(self.widget_heading)
        self.widget_steer_speed.addLegend((150, 5))

        self.widget_signal = self.graph.addPlot(1, 1)
        self.widget_signal.setTitle("driving mode")
        self.widget_signal.setLabel("bottom", "time [s]")
        self.widget_signal.showGrid(True, True)
        self.widget_signal.setXLink(self.widget_heading)
        self.widget_signal.addLegend((150, 5))
        #self.time_line_2 = widget_signal

        self.drive_mode = self.widget_signal.plot(name="drive_mode")
        self.stop_state = self.widget_signal.plot(name="stop_state")
        self.speed_fall_back = self.widget_signal.plot(name="speed_fall_back")
        self.path_fall_back = self.widget_signal.plot(name="path_fall_back")
        self.torque = self.widget_signal.plot(name= "torque")

        self.heding_refer = self.widget_heading.plot(name="heading_refer")
        self.heading_actual = self.widget_heading.plot(name="heading_actual")
        self.heading_planning = self.widget_heading.plot(name="heading_planning")

        self.steer_angle_refer = self.widget_steer.plot(name="steer_angle_refer")
        self.steer_angle_planing = self.widget_steer.plot(name="steer_angle_planing")
        self.steer_angle_actual = self.widget_steer.plot(name="steer_angle_actual")
        self.steer_angle_cmd = self.widget_steer.plot(name="steer_angle_cmd")

        self.steer_angle_speed_refer = self.widget_steer_speed.plot(name="steer_angle_speed_refer")
        self.steer_angle_speed_planing = self.widget_steer_speed.plot(name="steer_angle_speed_planing")
        self.steer_angle_speed_actual = self.widget_steer_speed.plot(name="steer_angle_speed_actual")

    def update_frame(self, frame):
        #print("planning_st:",self.planing," path_t_st:", ("path_t"in frame))
        if(self.planing and ("path_t"in frame)):
            self.steer_angle_speed_planing.setData(frame["path_t"],frame["steer_angle_speed"], pen=mkPen(color[5], width=2))
            self.steer_angle_planing.setData(frame["path_t"],frame["steer_angle"], pen=mkPen(color[5], width=2))
            self.heading_planning.setData(frame["path_t"],frame["heading_planning"], pen=mkPen(color[5], width=2))
        else:
            self.steer_angle_speed_planing.setData([],[], pen=mkPen(color[5], width=2))
            self.steer_angle_planing.setData([],[], pen=mkPen(color[5], width=2))
            self.heading_planning.setData([],[], pen=mkPen(color[5], width=2))
        self.widget_signal.enableAutoRange('xy', True)
        self.widget_heading.enableAutoRange('xy', True)
        self.widget_steer.enableAutoRange('xy', True)
        self.widget_steer_speed.enableAutoRange('xy', True) 

    def update_plot(self, data):
        self.heding_refer .setData(
            data["time"], data["heding_refer"], pen=mkPen(color[3], width=2))
        self.heading_actual .setData(
            data["time"], data["heading_actual"], pen=mkPen(color[1], width=2))

        self.steer_angle_speed_refer .setData(
            data["time"], data["steer_angle_speed_refer"], pen=mkPen(color[3], width=2))
        self.steer_angle_speed_actual .setData(
            data["time"], data["steer_angle_speed_actual"], pen=mkPen(color[1], width=2))

        self.steer_angle_refer.setData(
            data["time"], data["steer_angle_refer"], pen=mkPen(color[3], width=2))
        self.steer_angle_cmd.setData(
            data["time"], data["steer_angle_cmd"], pen=mkPen(color[2], width=2))
        self.steer_angle_actual.setData(data["time"],data["steer_angle_actual"], pen=mkPen(color[1], width=2))

        self.drive_mode.setData(
            data["time"], data["driving_mode"], pen=mkPen(color[0], width=2))
        self.stop_state.setData(
            data["time"], data["stop_state"], pen=mkPen(color[1], width=2))
        self.speed_fall_back.setData(data["time"], data["speed_fall_back"], pen=mkPen(
            color[3], width=2))
        self.path_fall_back.setData(data["time"], data["path_fall_back"], pen=mkPen(
            color[4], width=2))
        self.torque.setData(data["time"], data["torque"], pen=mkPen(
            color[5], width=2))


if __name__ == "__main__":
    app = QApplication([])
    m = LateralDebug()
    m.show()
    app.exec_()
