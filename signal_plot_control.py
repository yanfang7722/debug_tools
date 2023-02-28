from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from plot_singal_define import color_list, style_list,pen_list


class SignalPlotControlWidget(QWidget):
    widget_signal_dict_pyqt = pyqtSignal(dict)
    plotted_signal_name_list_pyqt = pyqtSignal(list)

    def __init__(self):
        super(SignalPlotControlWidget, self).__init__()
        self.all_signal_list = []
        self.filtered_signal_list = []
        self.widget_signal = {}
        self.choosed_signal = ""
        flo = QFormLayout()
        self.axis_x = QComboBox()
        self.axis_x.setEditable(True)
        self.axis_x.currentIndexChanged.connect(self.axis_x_selection_change)
        self.axis_y = QComboBox()
        self.axis_y.setEditable(True)
        self.axis_y.currentIndexChanged.connect(self.axis_y_selection_change)
        self.widget = QComboBox()
        self.widget.setEditable(True)
        self.widget.currentIndexChanged.connect(self.widget_selection_change)
        self.line_color = QComboBox()
        self.line_color.addItems(color_list)
        self.line_pen = QComboBox()
        self.line_pen.addItems(pen_list)
        self.line_pen.setEditable(True)
        self.line_style = QComboBox()
        self.line_style.addItems(style_list)
        self.line_style.setEditable(True)
        self.signal_name = QLineEdit(self)
        self.signal_name.setText("")
        self.signal_filter = QLineEdit(self)
        self.signal_filter.setText("")
        self.signal_filter.editingFinished.connect(self.update_filtered_signal)

        flo.addRow("widget", self.widget)
        flo.addRow("line_color", self.line_color)
        flo.addRow("line_pen", self.line_pen)
        flo.addRow("line_style", self.line_style)
        flo.addRow("signal filter", self.signal_filter)
        flo.addRow("signal name", self.signal_name)
        flo.addRow("axis x", self.axis_x)
        flo.addRow("axis y", self.axis_y)

        signal_action = QHBoxLayout()
        self.delete = QPushButton("删除")
        self.delete.clicked.connect(self.delete_plot)
        self.clear_widget = QPushButton("清空")
        self.clear_widget.clicked.connect(self.clear_widget_plot)
        self.add = QPushButton("添加")
        self.add.clicked.connect(self.add_plot)
        signal_action.addWidget(self.add)
        signal_action.addWidget(self.delete)
        signal_action.addWidget(self.clear_widget)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.list_item_choosed)

        layout = QVBoxLayout()
        layout.addLayout(flo)
        layout.addLayout(signal_action)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def update_axis_x_signal(self):
        print("update_axis_x_signal")
        self.axis_x.clear()
        self.axis_x.addItems(self.filtered_signal_list)

    def update_axis_y_signal(self):
        self.axis_y.clear()
        self.axis_y.addItems(self.filtered_signal_list)

    def list_item_choosed(self, data):
        print("choosed signal:", data.text())
        self.choosed_signal = data.text()
        for item in self.widget_signal[self.widget.currentText()]:
            if ("x:"+item[0] + "\n  y:"+item[1]) == self.choosed_signal:
                self.axis_x.setCurrentText(item[0])    
                self.axis_y.setCurrentText(item[1])    
                self.line_color.setCurrentText(item[2])
                self.line_pen.setCurrentText(item[3])
                self.line_style.setCurrentText(item[4])
                self.signal_name.setText(item[-1])

    def delete_plot(self):
        deleted_signal = {}
        deleted_signal[self.widget.currentText()] = []
        for item in self.widget_signal[self.widget.currentText()]:
            if ("x:"+item[0] + "\n  y:"+item[1]) != self.choosed_signal:
                deleted_signal[self.widget.currentText()].append(item)
        print("delete_plot:", deleted_signal)
        self.widget_signal[self.widget.currentText(
        )] = deleted_signal[self.widget.currentText()]
        print("add_plot", self.widget_signal[self.widget.currentText()])
        self.widget_selection_change(self.widget.currentText())
        self.widget_signal_dict_pyqt.emit(deleted_signal)
        self.update_plotted_signal_name_list()

    def clear_widget_plot(self):
        cleared_signal = {}
        cleared_signal[self.widget.currentText()] = []
        self.widget_signal[self.widget.currentText(
        )] = cleared_signal[self.widget.currentText()]
        print("clear widget signal ", self.widget.currentText())
        self.widget_selection_change(self.widget.currentText())
        self.widget_signal_dict_pyqt.emit(cleared_signal)
        self.update_plotted_signal_name_list()

    def add_plot(self):
        color_str = "a="+self.line_color.currentText()
        print(color_str)
        width_str = "b="+self.line_style.currentText()
        print(width_str)
        signal_added = [self.axis_x.currentText(), self.axis_y.currentText(), self.line_color.currentText(
        ), self.line_pen.currentText(), self.line_style.currentText(), self.signal_name.text()]
        if self.widget.currentText() not in self.widget_signal:
            self.widget_signal[self.widget.currentText()] = []
        self.widget_signal[self.widget.currentText()].append(signal_added)
        print("add_plot", self.widget_signal[self.widget.currentText()])
        self.widget_selection_change(self.widget.currentText())
        added_signal = {}
        added_signal[self.widget.currentText(
        )] = self.widget_signal[self.widget.currentText()]
        self.widget_signal_dict_pyqt.emit(added_signal)
        self.update_plotted_signal_name_list()

    def update_all_signal_name_list(self, data):
        self.all_signal_list.clear()
        print("update_all_signal_name_list,data ", data)
        self.all_signal_list = data
        self.axis_x.clear()
        self.axis_x.addItems(self.all_signal_list)
        self.axis_y.clear()
        self.axis_y.addItems(self.all_signal_list)

    def update_filtered_signal(self):
        filtered_str = self.signal_filter.text()
        print("filtered_str is ", filtered_str)
        if filtered_str == "":
            data = self.all_signal_list .copy()
            self.update_all_signal_name_list(data)
            return
        filtered_str_list = filtered_str.split(" ")
        self.filtered_signal_list = []
        for signal_name in self.all_signal_list:
            is_signal = True
            for item_str in filtered_str_list:
                if item_str not in signal_name:
                    is_signal = False
                    break
            if is_signal:
                self.filtered_signal_list.append(signal_name)

        current_axis_x = self.axis_x.currentText()
        current_axis_y = self.axis_y.currentText()
        print("current_axis_x:", current_axis_x)
        self.axis_x.clear()
        self.axis_x.addItems(self.filtered_signal_list)
        self.axis_x.addItem(current_axis_x)
        self.axis_y.clear()
        self.axis_y.addItems(self.filtered_signal_list)
        self.axis_y.addItem(current_axis_y)
        self.axis_x.setCurrentText(current_axis_x)
        self.axis_y.setCurrentText(current_axis_y)

    def update_y_filtered_signal(self, filtered_str):
        current_axis_x = self.axis_x.currentText()
        current_axis_y = self.axis_y.currentText()
        print("current_axis_x:", current_axis_x)
        self.axis_y.clear()
        self.axis_y.addItem(current_axis_y)
        topic_name = self.axis_x.currentText().split(".")[0]
        frame_signal_split = self.axis_x.currentText().split("[i]")
        is_frame = len(frame_signal_split) > 1
        for count in range(self.axis_x.count()):
            signal_name = self.axis_x.itemText(count)
            if topic_name not in signal_name:
                continue
            if is_frame and frame_signal_split[0] not in signal_name:
                continue
            self.axis_y.addItem(signal_name)

    def updata_tab_signal(self, data_widget):
        print("updata_tab_signal", data_widget)
        self.widget_signal.clear()
        for widget_name in data_widget:
            self.widget_signal[widget_name] = data_widget[widget_name]
        self.widget.clear()
        self.widget.addItems(self.widget_signal.keys())
        self.widget.setCurrentText(list(self.widget_signal.keys())[0])
        self.update_plotted_signal_name_list()

    def widget_edit_text_change(self, data):
        print("widget_edit_text_change", data)
        if data not in self.widget_signal.keys():
            self.widget_signal[data] = []
            added_signal = {}
            added_signal[self.widget.currentText(
            )] = self.widget_signal[self.widget.currentText()]
            self.widget_signal_dict_pyqt.emit(added_signal)
            return

    def axis_x_selection_change(self, i):
        print("axis_x_selection_change", self.axis_x.currentText())

    def axis_y_selection_change(self, i):
        print("axis_y_selection_change", self.axis_y.currentText())

    def widget_selection_change(self, i):
        data = self.widget.currentText()
        self.widget_edit_text_change(data)
        print("==========widget_selection_change========\n \"", data,"\":", self.widget_signal[data])
        self.list_widget.clear()
        widget_signal_list = ["x:"+it[0] + "\n  y:"+it[1]
                              for it in self.widget_signal[self.widget.currentText()]]
        self.list_widget.addItems(widget_signal_list)
        widget_signal_num = len(widget_signal_list)
        self.line_color.setCurrentText(color_list[widget_signal_num % 10])

    def update_plotted_signal_name_list(self):
        plotted_signal_name_set = set()
        for signal_list in self.widget_signal.values():
            for signal in signal_list:
                plotted_signal_name_set.add(signal[0])
                plotted_signal_name_set.add(signal[1])
        print("update_plotted_signal_name_list in signal plot",
              plotted_signal_name_set)
        self.plotted_signal_name_list_pyqt.emit(list(plotted_signal_name_set))


if __name__ == "__main__":
    app = QApplication([])
    demo = SignalPlotControlWidget()
    demo.show()
    app.exec_()
