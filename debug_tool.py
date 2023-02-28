# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from record_node import RecordNode
from graph_plot import GraphPlot
from plot_singal_define import *
from signal_plot_control import *
from table import *
import qdarkstyle


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabPosition(QTabWidget.South)
        self.tab = Tab()
        self.addTab(self.tab, "behavior table")
        for item in tab_list:
            creat_tab_str = "self."+item+"= GraphPlot("+item+")"
            add_tab_str = "self.addTab(self."+item+",\""+item+"\")"
            exec(creat_tab_str)
            exec(add_tab_str)
        self.new = GraphPlot({})
        self.addTab(self.new, "+")
        print("tab num is:", self.count())

    def add_new_graph(self):
        new_tab = GraphPlot({})
        self.insertTab(self.count()-1, new_tab, "tab"+str(self.count()))
        print("tab num is:", self.count())


class FrameControlWidget(QWidget):
    def __init__(self, parent=None):
        super(FrameControlWidget, self).__init__(parent)

        self.frame_id_slider = QSlider(Qt.Horizontal)
        self.frame_id_slider.setMaximum(-1)
        self.frame_id_slider.setMinimum(-1)
        self.frame_id_slider.setValue(-1)
        self.frame_id_slider.valueChanged.connect(self.update_spin_val)
        self.frame_id_spin = QSpinBox()
        self.frame_id_spin.setMaximum(-1)
        self.frame_id_spin.setMinimum(-1)
        self.frame_id_spin.setValue(-1)
        self.frame_id_spin.valueChanged.connect(self.update_slider_val)
        self.simulation = QCheckBox("Simulation")
        self.reset_data = QPushButton("Reset Data")

        frame_control_layout = QHBoxLayout()
        frame_control_layout.addWidget(QLabel("frame id"))
        frame_control_layout.addWidget(self.frame_id_slider)
        frame_control_layout.addWidget(self.frame_id_spin)
        frame_control_layout.addWidget(self.simulation)
        frame_control_layout.addWidget(self.reset_data)
        self.setLayout(frame_control_layout)

    def set_frame_id_range(self, data):
        print("self frame id length", data)
        self.frame_id_slider.setMinimum(-data)
        self.frame_id_spin.setMinimum(-data)

    def update_spin_val(self):
        self.frame_id_spin.setValue(self.frame_id_slider.value())
        print("spin_val_change:", self.frame_id_slider.value())
        # self.frame_id_signal.emit(self.frame_id_spin.value())

    def update_slider_val(self):
        self.frame_id_slider.setValue(self.frame_id_spin.value())
        print("slider_val_change:", self.frame_id_slider.value())

    def btnstate(self, btn):
        str_exec = "self." + btn.text() + " = " + str(btn.isChecked())
        exec(str_exec)


class MainWidget(QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setWindowTitle("Nio PNC Debug Tool（V2.1）")

        # 设置信号接收
        self.topic_thread = RecordNode()
        self.topic_thread.start()

        self.tab_widget = TabWidget()
        self.frame_control = FrameControlWidget()
        self.signal_plot_control = SignalPlotControlWidget()

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.signal_plot_control)
        self.splitter1.addWidget(self.tab_widget)
        print("splitter 1 size", self.splitter1.size())
        self.splitter1.setSizes([0, 1120, 0])
        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.frame_control)
        print("splitter 2  size", self.splitter2.size())
        self.splitter2.setSizes([2120, 1])
        self.setCentralWidget(self.splitter2)

        self.last_widget = self.tab_widget.motion_constrain_signal
        self.topic_thread.plotted_signal_data_pyqt.connect(
            self.last_widget.update_plot)
        self.signal_plot_control.widget_signal_dict_pyqt.connect(
            self.last_widget.reinit_widget_signal_list)
        self.topic_thread.all_signal_name_list_pyqt.connect(
            self.signal_plot_control.update_all_signal_name_list)
        self.topic_thread.history_length_pyqt.connect(
            self.frame_control.set_frame_id_range)
        self.tab_widget.currentChanged.connect(self.selectTab)
        self.tab_widget.setCurrentWidget(self.last_widget)
        self.frame_control.frame_id_spin.valueChanged.connect(
            self.topic_thread.reset_frame_id)
        self.frame_control.reset_data.clicked.connect(
            self.topic_thread.reset_data)
        self.signal_plot_control.plotted_signal_name_list_pyqt.connect(
            self.topic_thread.update_plotted_signal_list)
        self.selectTab(1)

    def selectTab(self, p):
        self.signal_plot_control.widget_signal_dict_pyqt.disconnect(
            self.last_widget.reinit_widget_signal_list)
        self.topic_thread.plotted_signal_data_pyqt.disconnect(
            self.last_widget.update_plot)
        self.last_widget = self.tab_widget.currentWidget()
        self.topic_thread.plotted_signal_data_pyqt.connect(
            self.last_widget.update_plot)
        self.signal_plot_control.widget_signal_dict_pyqt.connect(
            self.last_widget.reinit_widget_signal_list)
        if p > 0:
            self.signal_plot_control.updata_tab_signal(
                self.last_widget.data_widget)
        if p == self.tab_widget.count()-1:
            self.tab_widget.add_new_graph()
        self.topic_thread.emit_signal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWidget()
    print(main.layout())
    main.show()
    sys.exit(app.exec_())
