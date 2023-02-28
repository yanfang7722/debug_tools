#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from unicodedata import name
from PyQt5 import QtCore

from pyqtgraph.functions import mkBrush, mkPen
from PyQt5.QtWidgets import *
import numpy as np
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget


class PlanningDynamic(QWidget):
    def __init__(self):
        super(PlanningDynamic, self).__init__()
        self.graph = GraphicsLayoutWidget()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.graph)
        self.slwidget = self.graph.addPlot(0, 0)
        self.slwidget.setTitle('<font size="4">sl_bound</font>')
        self.slwidget.setLabel("left", "l")
        self.slwidget.setLabel("bottom", "s")
        self.slwidget.addLegend((150, 0.2))
        self.slwidget.showGrid(True, True)
        self.slwidgetUpperCurve = self.slwidget.plot()
        self.slwidgetLowerCurve = self.slwidget.plot()
        self.slwidgetCrossUpperCurve = self.slwidget.plot(name="cross_bound")
        self.slwidgetCrossLowerCurve = self.slwidget.plot()
        self.slwidgetNudgeUpperCurve = self.slwidget.plot(name="nudge_bound")
        self.slwidgetNudgeLowerCurve = self.slwidget.plot()
        self.slwidgetMotionCurve = self.slwidget.plot()
        self.slwidgetBehaviorCurve = self.slwidget.plot()

        self.thetaswidget = self.graph.addPlot(1, 0)
        self.thetaswidget.showGrid(True, True)
        self.thetaswidget.setLabel("left", "theta")
        self.thetaswidget.setLabel("bottom", 's')
        self.thetaswidget.addLegend((150,0.2))
        self.thetaswidget.setTitle('<font size="4">theta_s</font>')
        self.thetaswidgetcurve = self.thetaswidget.plot()
        self.thetaswidgetbcurve = self.thetaswidget.plot()
        self.dl_s = self.thetaswidget.plot(name="dl")

        self.kswidget = self.graph.addPlot(2, 0)
        self.kswidget.showGrid(True, True)
        self.kswidget.setLabel("left", "kappa")
        self.kswidget.setLabel("bottom", "s")
        self.kswidget.addLegend((150,0.2))
        self.kswidget.setTitle('<font size="4">kappa_s</font>')
        self.kswidgetcurve = self.kswidget.plot(name = "kappa")
        self.kswidgetbcurve = self.kswidget.plot()
        self.dkswidgetcurve = self.kswidget.plot(name = "dkappa")
        self.ddl_s = self.kswidget.plot(name="ddl")

        self.stwidget = self.graph.addPlot(0, 1)
        self.stwidget.showGrid(True, True)
        self.stwidget.setLabel("left", "s")
        self.stwidget.setLabel("bottom", "t")
        self.stwidget.addLegend((150, 0.2))
        self.stwidget.setTitle('<font size="4">st_bound</font>')
        self.stwidgetLowerCurve = self.stwidget.plot(name="hard_bound")
        self.stwidgetUpperCurve = self.stwidget.plot()
        self.stwidgetMotionCurve = self.stwidget.plot(name="motion")
        self.stwidgetBehaviorCurve = self.stwidget.plot(name="behavior")
        self.pos_s = self.stwidget.plot(name = "pos_s")

        self.vtwidget = self.graph.addPlot(1, 1)
        self.vtwidget.showGrid(True, True)
        self.vtwidget.setLabel("left", "v")
        self.vtwidget.setLabel("bottom", 't')
        self.vtwidget.addLegend((150,0.2))
        self.vtwidget.setTitle('<font size="4">v_t</font>')
        self.vtwidgetcurve = self.vtwidget.plot()
        self.vtwidgetbcurve = self.vtwidget.plot()
        self.speed_planning = self.vtwidget.plot(name = "speed_planning")
    

        self.atwidget = self.graph.addPlot(2, 1)
        self.atwidget.showGrid(True, True)
        self.atwidget.setLabel("left", "a")
        self.atwidget.setLabel("bottom", "t")
        self.atwidget.addLegend((150,0.2))
        self.atwidget.setTitle('<font size="4">a_t</font>')
        self.atwidgetcurve = self.atwidget.plot()
        self.atwidgetbcurve = self.atwidget.plot()
        # self.obs_decision = self.atwidget.plot(name="obs_decision")
        self.acc_lon_planning = self.atwidget.plot(name = "acc_lon_planning")
        self.acc_lat_planning = self.atwidget.plot(name = "acc_lat_planning")
        # self.path_jerk_lon = self.atwidget.plot(name = "path_acc_lon")
        self.jerk_lat_planning = self.atwidget.plot(name = "jerk_lat_planning")
        
        self.s_range =[]

    def SetSLMinMaxY(self):
        self.slwidget.enableAutoRange('xy', True)
        self.thetaswidget.enableAutoRange('xy', True)
        self.kswidget.enableAutoRange('xy', True)
        self.stwidget.enableAutoRange('xy', True)
        self.vtwidget.enableAutoRange('xy', True)
        self.atwidget.enableAutoRange('xy', True)

    def update(self, data):
        color = ['y',  'b',  'g', 'm', [139, 105, 20], 'r',[255,165,0],[0,255,255],[255,165,0]]
        frame = data
        self.slwidgetMotionCurve.setData(
           frame["pos_s_path"], frame["pos_l_path"], pen=mkPen(color[2], width=2))
        self.thetaswidgetcurve.setData(
           frame["pos_s_path"], frame["theta_path"],pen=mkPen(color[2], width=2))
        self.kswidgetcurve.setData(
            frame["pos_s_path"], frame["kappa_path"],pen=mkPen(color[2], width=2))
        self.dkswidgetcurve.setData(
            frame["pos_s_path"], frame["dkappa_path"],pen=mkPen(color[3], width=2))
        self.dl_s.setData(
            frame["pos_s_path"], frame["pos_dl_path"],pen=mkPen(color[4], width=2))
        self.ddl_s.setData(
            frame["pos_s_path"], frame["pos_ddl_path"],pen=mkPen(color[5], width=2))
        self.pos_s.setData(
            frame["path_t"],frame["pos_s_path"], pen=mkPen(color[2], width=2))
        self.speed_planning.setData(
            frame["path_t"],frame["speed_path"], pen=mkPen(color[3], width=2))
        self.acc_lon_planning.setData(
            frame["path_t"],frame["acc_lon_path"], pen=mkPen(color[3], width=2))
        self.acc_lat_planning.setData(
            frame["path_t"],frame["acc_lat_path"], pen=mkPen(color[4], width=2))
        self.jerk_lat_planning.setData(
            frame["path_t"],frame["jerk_lat_path"], pen=mkPen(color[5], width=2))
        if("obs_decision_t" in frame):
             self.obs_decision.setData(
            frame["obs_decision_t_path"],frame["obs_decision_path"], pen=mkPen(color[5], width=2))
        if("SpeedPoint"in data):
            # SpeedPoint: t, s, v, a
            SpeedPoint = np.array(data["SpeedPoint"])
            if(SpeedPoint.shape[0] > 0):
                self.stwidgetMotionCurve.setData(
                    y=SpeedPoint[:, 1], x=SpeedPoint[:, 0], pen=mkPen(color[2], width=2))
                self.vtwidgetcurve.setData(
                    y=SpeedPoint[:, 2], x=SpeedPoint[:, 0], pen=mkPen(color[2], width=2))
                self.atwidgetcurve.setData(
                    y=SpeedPoint[:, 3], x=SpeedPoint[:, 0], pen=mkPen(color[2], width=2))

        if("PathPoint"in data):
            # PathPoint: s , l, theta, k
            PathPoint = np.array(data["PathPoint"])
            # BehaviorPoint: pb.s,pb.k,pb.theta,pb.t,pb.l,pb.speed,pb.acceleration
            BehaviorPoint = np.array(data["BehaviorPoint"])
            if(PathPoint.shape[0] > 0):
                self.slwidgetMotionCurve.setData(
                    y=PathPoint[:, 1], x=PathPoint[:, 0], pen=mkPen(color[2], width=2))
                self.thetaswidgetcurve.setData(
                    y=PathPoint[:, 2], x=PathPoint[:, 0], pen=mkPen(color[2], width=2))
                self.kswidgetcurve.setData(
                    y=PathPoint[:, 3], x=PathPoint[:, 0], pen=mkPen(color[2], width=2))
            if(BehaviorPoint.shape[0] > 0):
                self.slwidgetBehaviorCurve.setData(
                    y=BehaviorPoint[:, 4], x=BehaviorPoint[:, 0], pen=mkPen(color[1], width=2))
                self.stwidgetBehaviorCurve.setData(
                    y=BehaviorPoint[:, 0], x=BehaviorPoint[:, 3], pen=mkPen(color[1], width=2))
                self.vtwidgetbcurve.setData(
                    y=BehaviorPoint[:, 5], x=BehaviorPoint[:, 3], pen=mkPen(color[1], width=2))
                self.atwidgetbcurve.setData(
                    y=BehaviorPoint[:, 6], x=BehaviorPoint[:, 3], pen=mkPen(color[1], width=2))
                self.thetaswidgetbcurve.setData(
                    y=BehaviorPoint[:, 2], x=BehaviorPoint[:, 0], pen=mkPen(color[1], width=2))
                self.kswidgetbcurve.setData(
                    y=BehaviorPoint[:, 1], x=BehaviorPoint[:, 0], pen=mkPen(color[1], width=2))

                    # SignalSequence: t, path_fall_back_type, speed_fall_back_type
#        SignalSequence = np.array(data["SignalSequence"])
        if(len(data["SLR"]["s"]) > 0):
            print("updating dynamic planning",data["SpeedPoint"][0])
            self.slwidgetUpperCurve.setData(
                y=data["SLR"]["hard_ub"], x=data["SLR"]["s"], pen=mkPen(color[0], width=2))
            self.slwidgetLowerCurve.setData(
                y=data["SLR"]["hard_lb"], x=data["SLR"]["s"], pen=mkPen(color[0], width=2))

            self.slwidgetCrossUpperCurve.setData(y=data["SLR"]["crossable_ub"], x=data["SLR"]["s"], pen=mkPen(
                color[3], width=1, style=QtCore.Qt.DashLine))
            self.slwidgetCrossLowerCurve.setData(y=data["SLR"]["crossable_lb"], x=data["SLR"]["s"], pen=mkPen(
                color[3], width=1, style=QtCore.Qt.DashLine))
            self.slwidgetNudgeUpperCurve.setData(y=data["SLR"]["obs_nudge_ub"], x=data["SLR"]["s"], pen=mkPen(
                color[4], width=1, style=QtCore.Qt.DashLine))
            self.slwidgetNudgeLowerCurve.setData(y=data["SLR"]["obs_nudge_lb"], x=data["SLR"]["s"], pen=mkPen(
                color[4], width=1, style=QtCore.Qt.DashLine))
        
        if(len(data["STR"]["t"]) > 0):
            self.stwidgetLowerCurve.setData(
                y=data["STR"]["hard_ub"], x=data["STR"]["t"], pen=mkPen(color[0], width=2))
            self.stwidgetUpperCurve.setData(
                y=data["STR"]["hard_lb"], x=data["STR"]["t"], pen=mkPen(color[0], width=2))
        self.SetSLMinMaxY()




if __name__ == "__main__":
    app = QApplication([])
    m = PlanningDynamic()
    m.stwidget.close()
    m.show()
    app.exec_()
