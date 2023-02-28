#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import name
import sys
from PyQt5 import QtCore
from numpy.lib.function_base import _update_dim_sizes
from pyqtgraph.functions import mkBrush, mkPen
from PyQt5.QtWidgets import *
import numpy as np
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget


class PlanningSLT(QWidget):
    def __init__(self):
        super(PlanningSLT, self).__init__()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdateSLTCube)
        self.graph = GraphicsLayoutWidget()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.graph)
        # self.slider =QSlider(Qt.Horizontal)
        self.data = {}

        self.sltCubeWidget_3 = self.graph.addPlot(0, 0)
        self.sltCubeWidget_3.showGrid(True, True)
        self.sltCubeWidget_3.setLabel("left", "l")
        self.sltCubeWidget_3.setLabel("bottom", "s")
        self.sltCubeWidget_3.setTitle('<font size="4">slt_cube_sl</font>')

        self.sltCubeWidget_2 = self.graph.addPlot(1, 1)
        self.sltCubeWidget_2.showGrid(True, True)
        self.sltCubeWidget_2.setLabel("left", "s")
        self.sltCubeWidget_2.setLabel("bottom", "t")
        self.sltCubeWidget_2.setTitle('<font size="4">slt_cube_ts</font>')

        self.sltCubeWidget_1 = self.graph.addPlot(0, 1)
        self.sltCubeWidget_1.showGrid(True, True)
        self.sltCubeWidget_1.setLabel("left", "l")
        self.sltCubeWidget_1.setLabel("bottom", "t")
        self.sltCubeWidget_1.setTitle('<font size="4">slt_cube_tl</font>')

        self.slwidget = self.sltCubeWidget_3
        self.stwidget = self.sltCubeWidget_2

        self.SignalSequence = self.graph.addPlot(1, 0)
        self.SignalSequence.showGrid(True, True)
        self.SignalSequence.setLabel("left", "signal")
        self.SignalSequence.setLabel("bottom", "frame_id")
        self.SignalSequence.addLegend((150, 0.2))
        self.SignalSequence.setTitle('<font size="4">signal_sequence</font>')
        self.speed_fall_back = self.SignalSequence.plot(name="speed_fall_back")
        self.path_fall_back = self.SignalSequence.plot(name="path_fall_back")
        self.stop_state = self.SignalSequence.plot(name="stop_state")
    
    def SetSLMinMaxY(self, data):
        min_val = 10
        max_val = -10
        min_s = sys.float_info.max
        max_s = sys.float_info.min

    def UpdateSLTCube(self):
    
        if not ("Cube"  in self.data): 
            print("cube is empty")
            return
        Cube = self. data["Cube"]
        self.sltCubeWidget_1.clear()
        self.sltCubeWidget_2.clear()
        self.sltCubeWidget_3.clear()
        print("Cube len",  len(Cube))
        if(len(Cube) < 1):
            return

        for i, item in enumerate(Cube):
            # print(" update stl cube dynamic ", item)
            self.sltCubeWidget_1.plot(item[2], item[1], pen=mkPen(
                item[4], width=2, style=QtCore.Qt.DashLine))  # tl
            self.sltCubeWidget_2.plot(item[2], item[0], pen=mkPen(
                item[4], width=2, style=QtCore.Qt.DashLine))  # ts
            self.sltCubeWidget_3.plot(item[3], item[1], pen=mkPen(
                item[4], width=2, style=QtCore.Qt.DashLine))  # sl

        self.updata_signal()

    def updata_data(self, data):
        print("update slt data")
        self.data = data
    
    def updata_signal(self):
        print("update slt map")
        data = self.data
        # PathPoint: s , l, theta, k
        PathPoint = np.array(data["PathPoint"])
        # SpeedPoint: t, s, v, a
        SpeedPoint = np.array(data["SpeedPoint"])
        # BehaviorPoint: pb.s,pb.k,pb.theta,pb.t,pb.l,pb.speed,pb.acceleration
        BehaviorPoint = np.array(data["BehaviorPoint"])
        color = ['r',  'b',  'g', 'm', [139, 105, 20], 'k']

        # self.slwidgetUpperCurve = self.slwidget.plot()
        # self.slwidgetLowerCurve = self.slwidget.plot()
        # self.slwidgetCrossUpperCurve = self.slwidget.plot(name="cross_bound")
        # self.slwidgetCrossLowerCurve = self.slwidget.plot()
        # self.slwidgetNudgeUpperCurve = self.slwidget.plot(name="nudge_bound")
        # self.slwidgetNudgeLowerCurve = self.slwidget.plot()
        # self.slwidgetMotionCurve = self.slwidget.plot()
        # self.slwidgetBehaviorCurve = self.slwidget.plot()
        # self.slwidgetUpperCurve.setData(
        #     y=data["SLR"]["hard_ub"], x=data["SLR"]["s"], pen=mkPen(color[0], width=2))
        # self.slwidgetLowerCurve.setData(
        #     y=data["SLR"]["hard_lb"], x=data["SLR"]["s"], pen=mkPen(color[0], width=2))
        # self.slwidgetCrossUpperCurve.setData(y=data["SLR"]["crossable_ub"], x=data["SLR"]["s"], pen=mkPen(
        #     color[3], width=1))
        # self.slwidgetCrossLowerCurve.setData(y=data["SLR"]["crossable_lb"], x=data["SLR"]["s"], pen=mkPen(
        #     color[3], width=1))
        # self.slwidgetNudgeUpperCurve.setData(y=data["SLR"]["obs_nudge_ub"], x=data["SLR"]["s"], pen=mkPen(
        #     color[4], width=1))
        # self.slwidgetNudgeLowerCurve.setData(y=data["SLR"]["obs_nudge_lb"], x=data["SLR"]["s"], pen=mkPen(
        #     color[4], width=1))
        # self.SetSLMinMaxY(data["Cube"])

        self.stwidgetLowerCurve = self.stwidget.plot(name="hard_bound")
        self.stwidgetUpperCurve = self.stwidget.plot()
        self.stwidgetMotionCurve = self.stwidget.plot(name="motion")
        self.stwidgetBehaviorCurve = self.stwidget.plot(name="behavior")

        if(len(data["STR"]["t"]) > 0):
            self.stwidgetLowerCurve.setData(
                y=data["STR"]["hard_ub"], x=data["STR"]["t"], pen=mkPen(color[0], width=2))
            self.stwidgetUpperCurve.setData(
                y=data["STR"]["hard_lb"], x=data["STR"]["t"], pen=mkPen(color[0], width=2))

        if(SpeedPoint.shape[0] > 0):
            self.stwidgetMotionCurve.setData(
                y=SpeedPoint[:, 1], x=SpeedPoint[:, 0], pen=mkPen(color[2], width=2))

        # if(PathPoint.shape[0] > 0):
        #     self.slwidgetMotionCurve.setData(
        #         y=PathPoint[:, 1], x=PathPoint[:, 0], pen=mkPen(color[2], width=2))
        if(BehaviorPoint.shape[0] > 0):
            # self.slwidgetBehaviorCurve.setData(
            #     y=BehaviorPoint[:, 4], x=BehaviorPoint[:, 0], pen=mkPen(color[1], width=2))
            self.stwidgetBehaviorCurve.setData(
                y=BehaviorPoint[:, 0] , x=BehaviorPoint[:, 3], pen=mkPen(color[1], width=2))


if __name__ == "__main__":
    app = QApplication([])
    m = PlanningSLT()
    m.show()
    app.exec_()
