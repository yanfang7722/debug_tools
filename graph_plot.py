#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from os import name
from PyQt5.QtCore import *
from numpy.core.fromnumeric import shape
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from PyQt5.QtWidgets import *
from pyqtgraph.functions import mkPen
from plot_singal_define import color_list, pen_list, style_list
import pyqtgraph as pg


class GraphPlot(QWidget):
    def __init__(self, data_widget):
        super(GraphPlot, self).__init__()
        self.graph = GraphicsLayoutWidget()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.graph)
        self.data_widget = data_widget
        self.data = {}

        for widget_name in data_widget:
            signal_name_list = data_widget[widget_name]
            print(widget_name, ":", signal_name_list)
            self.update_widget_signal_list(widget_name, signal_name_list)

    def update_widget_signal_list(self, widget_name, signal_name_list):
        vb = CustomViewBox()
        widget_pos_str = widget_name.split("_")
        titel = widget_name[0:-4]
        widget_pos = widget_pos_str[-2]+","+widget_pos_str[-1]
        plot_widget = "self."+widget_name + \
            " = self.graph.addPlot("+widget_pos+",viewBox= vb)"
        exec(plot_widget)
        legend_str = "self."+widget_name+".addLegend((100, 5))"
        exec(legend_str)
        grid_str = "self."+widget_name+".showGrid(True, True)"
        exec(grid_str)
        title_str = "self."+widget_name + \
            ".setTitle('<font size=\"4\">"+titel+"</font>')"
        exec(title_str)
        for signal_name in signal_name_list:
            if (signal_name[0] == "" or signal_name[1] == ""):
                continue
            if signal_name[-1] == "":
                legend_name = signal_name[1]
            else:
                legend_name = signal_name[-1]
            # name_str_0 = signal_name[0].replace(".","_").replace("[","_").replace("]","_")
            name_str_1 = signal_name[1].replace(
                ".", "_").replace("[", "_").replace("]", "_")
            signal_plot_str = "self."+name_str_1 + " =self."+widget_name + \
                ".plot(name=\""+legend_name+"\",pen=pg.mkPen(" + signal_name[3]+"color=" +\
                signal_name[2]+")"+signal_name[4]+")"
            # print("signal_plot_str===\n",signal_plot_str)
            exec(signal_plot_str)

    def reinit_widget_signal_list(self, data_widget):
        for widget_name in data_widget:
            widget_pos_str = widget_name.split("_")
            if not (widget_pos_str[-1].isnumeric() and widget_pos_str[-2].isnumeric()):
                continue
            if widget_name in self.data_widget.keys():
                clear_widget_str = "self."+widget_name+".close()"
                exec(clear_widget_str)
                remove_widget_str = "self.graph.removeItem(self." + \
                    widget_name+")"
                exec(remove_widget_str)
            self.data_widget[widget_name] = data_widget[widget_name]
            self.update_widget_signal_list(
                widget_name, self.data_widget[widget_name])
        self.update_plot(self.data)

    def update_plot(self, data):
        self.data = data
        for widget_name in self.data_widget:
            for signal_name in self.data_widget[widget_name]:
                print(signal_name)
                try:
                    if type(data[signal_name[0]][0]) not in (int, float):
                        print("graph plot0", widget_name, signal_name[0], " type error", type(
                            data[signal_name[0]][0]))
                        continue
                    if type(data[signal_name[1]][0]) not in (int, float):
                        print("graph plot0", widget_name, signal_name[1], " type error", type(
                            data[signal_name[1]][0]))
                        continue
                    if len(data[signal_name[0]]) != len(data[signal_name[1]]):
                        print("graph plot1 length unequal")
                        print("graph plot1", widget_name, signal_name[0], " size is:", len(
                            data[signal_name[0]]))
                        print("graph plot1", widget_name, signal_name[1], " size is:", len(
                            data[signal_name[1]]))
                        continue
                except IndexError:
                    print(signal_name)
                    print("graph plot x size : ", len(data[signal_name[0]]), "y size:", len(data[signal_name[1]]))
                except KeyError:
                    print("graph plot3", widget_name,
                          signal_name[0], " is in data:", signal_name[0] in data)
                    print("graph plot3", widget_name,
                          signal_name[1], " is in data:", signal_name[1] in data)
                except ValueError:
                    print("graph plot4", widget_name, signal_name[0], " type error", type(
                        data[signal_name[0]][0]))
                    print("graph plot4", widget_name, signal_name[1], " type error", type(
                        data[signal_name[1]][0]))
                else:
                    name_str_1 = signal_name[1].replace(
                        ".", "_").replace("[", "_").replace("]", "_")
                    update_signal_str = "self."+name_str_1 + \
                        ".setData(data[\""+signal_name[0] + \
                        "\"],data[\""+signal_name[1]+"\"])"
                    exec(update_signal_str)


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    # reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.enableAutoRange('xy', True)

    def mouseDragEvent(self, ev):
        if ev.button() == Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)
            self.enableAutoRange('x', True)


if __name__ == "__main__":
    app = QApplication([])
    data_str = {
        "widget_0_0": [
            ["car_state.time_meas", "car_state.speed", color_list[0], "1"],
            ["car_state.time_meas",
                "control_command.simple_debug.speed_reference", color_list[1], "1"],
            ["car_state.time_meas", "control_command.simple_debug.speed",
                color_list[2], "1"],
        ],
        "widget_1_0": [
            ["car_state.time_meas", "car_state.longitudinal_acceleration",
                color_list[0], "1"],
            ["car_state.time_meas", "control_command.acceleration", color_list[1], "1"],
            ["car_state.time_meas",
                "control_command.simple_debug.acceleration_cmd", color_list[2], "1"],
        ],
        "widget_1_1": [
            ["path.time_meas", "path.stop_state", color_list[0], "1"],
            ["path.path_points[i].t", "path.path_points[i].ddl", color_list[1], "1"],
        ],
    }
    m = GraphPlot(data_str)
    update = {"widget_1_0": [["time", "acceleration", " [0, 0, 255]", "2"], [
        "time", "ego_lon_acc", "[0, 255, 0]", "2"]]}
    m.reinit_widget_signal_list(update)
    m.show()
    app.exec_()
