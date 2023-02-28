from PyQt5.QtWidgets import QApplication, QHBoxLayout, QTableWidget, QTableWidgetItem, QWidget


class Tab(QWidget):
    def __init__(self):
        super(Tab,self).__init__()
        self.tabwidget=QTableWidget(self)
        self.main_layout=QHBoxLayout(self)
        self.main_layout.addWidget(self.tabwidget)
        self.setLayout(self.main_layout)
        self.setHead()
        
    def reinit_widget_signal_list(self):
        return

    def setHead(self):
        self.tabwidget.setRowCount(28)
        self.tabwidget.setColumnCount(7)
        self.tabwidget.setHorizontalHeaderLabels(['seq_id','action','efficiency_cost','safety_cost','navigation_cost','utility_cost','final_cost'])

    def update_plot(self, data_all):
        data = data_all["debug_info.BehaviorDebug"]
        self.tabwidget.clearContents()
        def takeSecond(elem):
            return elem[6]
        data.sort(key=takeSecond)
        for index, line in enumerate(data):
            newItem1 = QTableWidgetItem(str(line[0]))
            self.tabwidget.setItem(index, 0, newItem1)
            newItem2 = QTableWidgetItem(str(line[1]))
            self.tabwidget.setItem(index, 1, newItem2)
            newItem3 = QTableWidgetItem(str(line[2]))
            self.tabwidget.setItem(index, 2, newItem3)
            newItem4 = QTableWidgetItem(str(line[3]))
            self.tabwidget.setItem(index, 3, newItem4)
            newItem5 = QTableWidgetItem(str(line[4]))
            self.tabwidget.setItem(index, 4, newItem5)
            newItem6 = QTableWidgetItem(str(line[5]))
            self.tabwidget.setItem(index, 5, newItem6)
            newItem7 = QTableWidgetItem(str(line[6]))
            self.tabwidget.setItem(index, 6, newItem7)

if __name__=="__main__":
    app=QApplication([])
    t=Tab()
    plotted_data={}
    plotted_data["debug_info.BehaviorDebug"]=[
        [0, "MMMMMM|KKKKKK", 0.007349285968642211, 0.0, 11.865425185942756, 0.0, 11.8727744719114],
        [1, "MAAAAA|KKKKKK", 0.007349285968642211, 0.0, 11.865425185942756, 0.0, 11.8727744719114],
        [2, "MDDDDD|KKKKKK", 2.9434934647264956, 0.0, 11.865425185942756, 0.0, 14.808918650669252],
        [3, "MAAAAA|KFFFFF", 4.801528591651165, 0.0, 0.0, 0.0, 1.7976931348623157e308],
    ]
    t.update_plot(plotted_data)
    t.show()
    app.exec_()