import sys
import os
AWFM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, AWFM_ROOT)

from PyQt5.QtWidgets import QDialog, QApplication, QTableWidget, QDialogButtonBox, \
        QDialogButtonBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog, \
        QMessageBox
from PyQt5.QtGui import QIcon

import awfm.core
import awfm.core.io

class EditWellsDlg(QDialog):
    def __init__(self, model, parent=None):
        super(EditWellsDlg, self).__init__(parent)
        self.model = model
        self.initWidgets()
        self.initLayout()
        self.resize(800, 500)
        self.setWindowTitle("Edit Wells")

    def addNewWell(self):
        well_name, ok = QInputDialog.getText(self, 'Add New Well', 'Well Name: ')
        if ok:
            if well_name in self.model.well_names():
                QMessageBox.information(self, "Name taken", \
                    "Wells must have unique names. Please choose a different name.")
            elif well_name == "":
                QMessageBox.information(self, "Empty name", \
                    "A well name cannot be an empty string.")
            else:
                self.model.wells[well_name] = awfm.core.Well(well_name, 0, 0)
                self.refreshTable()
            

    def addWellToTable(self, well_name, x, y, rw, h0):
        last_row = self.table.rowCount()
        self.table.insertRow(last_row)
        self.table.setCellWidget(last_row, 0, QLabel(well_name))

    def deleteWells(self):
        model_indices = self.table.selectionModel().selectedRows()
        for model_index in model_indices:
            well_name = self.table.cellWidget(model_index.row(), 0).text()
            del self.model.wells[well_name]
        self.refreshTable()

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        headers_tooltips = {
            "Name": "Name of well. Must be a unique identifier",
            "X": "X coordinate in %s" %self.model.units["length"],
            "Y": "Y coordinate in %s" %self.model.units["length"],
            "Rw": "Casing radius in %s" %self.model.units["length"],
            "H0": "Water level at model start time in %s" %self.model.units["length"],
            "DH/DT": "Change in water level per unit time in %s per %s" \
                %(self.model.units["length"], self.model.units["time"])
        }
        headers = ('Name', 'X', 'Y', 'Rw', 'H0', 'DH/DT')
        self.table.setHorizontalHeaderLabels(headers)

        for idx, header in enumerate(headers):
            tooltip = headers_tooltips[header]
            item = self.table.horizontalHeaderItem(idx)
            item.setToolTip(tooltip)
        self.refreshTable()

    def initWidgets(self):
        self.initTable()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                        | QDialogButtonBox.Cancel);
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.addWellButton = QPushButton("")
        self.addWellButton.setIcon(QIcon("icons/plus.svg"))
        self.addWellButton.setToolTip("Add new well")
        self.addWellButton.clicked.connect(self.addNewWell)

        self.deleteWellButton = QPushButton("")
        self.deleteWellButton.setIcon(QIcon("icons/trash.svg"))
        self.deleteWellButton.setToolTip("Delete selected well(s)")
        self.deleteWellButton.clicked.connect(self.deleteWells)

        self.importButton = QPushButton("Import")
        self.importButton.setToolTip("Import wells from CSV, Excel, or SQLite")


    def initLayout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.addWellButton)
        bottom_layout.addWidget(self.deleteWellButton)
        bottom_layout.addWidget(self.importButton)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.buttonBox)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def refreshTable(self):
        self.table.setRowCount(0)
        wells = self.model.wells
        for well_name in list(sorted(wells.keys())):
            w = wells[well_name]
            self.addWellToTable(well_name, w.x, w.y, w.rw, w.h0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = EditWellsDlg(awfm.core.Model())
    dlg.show()
    sys.exit(app.exec_())
    