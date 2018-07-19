import sys
import os
AWFM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, AWFM_ROOT)

from PyQt5.QtWidgets import QDialog, QApplication, QTableWidget, QDialogButtonBox, \
        QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox

import awfm.core
import awfm.core.io


class UnitsDlg(QDialog):
    def __init__(self, initial_units, parent=None):
        super(UnitsDlg, self).__init__(parent)
        self.initial_units = initial_units
        self.init()

    def init(self):
        grid = QGridLayout()
        units = awfm.core.units.UNITS
        self.comboBoxes = {}
        for row, unit_type in enumerate(["length", "time", "discharge"]):
            self.comboBoxes[unit_type] = QComboBox()
            self.comboBoxes[unit_type].addItems(units[unit_type].keys())
            grid.addWidget(QLabel(unit_type), row, 0)
            grid.addWidget(self.comboBoxes[unit_type], row, 1)
            index = self.comboBoxes[unit_type].findText(self.initial_units[unit_type])
            self.comboBoxes[unit_type].setCurrentIndex(index)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                        | QDialogButtonBox.Cancel);
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid)
        main_layout.addWidget(self.buttonBox)
        self.setLayout(main_layout)

    def updatedUnits(self):
        units = {}
        for unit_type in self.comboBoxes.keys():
            units[unit_type] = self.comboBoxes[unit_type].currentText()
        return units

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = UnitsDlg(awfm.core.Model().units)
    dlg.show()
    sys.exit(app.exec_())
    