import sys
import os
AWFM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, AWFM_ROOT)

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, \
    QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon

import awfm.core
import awfm.core.io

from editwellsdlg import EditWellsDlg
from unitsdlg import UnitsDlg


class AWFMMainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.model = None
        self.actions = self.initActions()
        self.initUI()

        self.setDirty(False)
        self.setModelLoaded(False)
        self.saveFileName = None

       
    def createAction(self, text, slot, shortcut=None, icon_path=None, status_tip=None):
        if icon_path:
            act = QAction(QIcon(icon_path), text, self)
        else:
            act = QAction(text, self)

        if shortcut:
            act.setShortcut(shortcut)

        if status_tip:
            act.setStatusTip(status_tip)

        act.triggered.connect(slot)
        return act

    def dummyAction(self):
        pass

    def editUnits(self):
        dlg = UnitsDlg(self.model.units, self)
        if dlg.exec_():
            self.model.units = dlg.updatedUnits()

    def editWells(self):
        dlg = EditWellsDlg(self.model, self)
        dlg.show()
        
    def initActions(self):
        actions = {
            "File->New": self.createAction("&New", self.new, shortcut="Ctrl+N"),
            "File->Open": self.createAction("&Open", self.open, shortcut="Ctrl+O"),
            "File->Save": self.createAction("&Save", self.save, shortcut="Ctrl+S"),
            "File->Save As": self.createAction("Save As", self.saveAs),
            "File->Quit": self.createAction("&Quit", self.quit, shortcut="Ctrl+Q"),
            "Model->Units": self.createAction("&Units", self.editUnits, shortcut="Ctrl+U"),
            "Model->Wells": self.createAction("&Wells", self.editWells, shortcut="Ctrl+W"),
            "Model->Aquifer Drawdown": self.createAction("&Aquifer Drawdown", self.dummyAction),
            "Model->Well Loss": self.createAction("Well &Loss", self.dummyAction),
            "Model->Pumping Rates": self.createAction("&Pumping Rates", self.dummyAction),
            "Model->Run": self.createAction("&Run", self.dummyAction, icon_path='icons/play.svg'),
            "Parameter Estimation->Water Levels": self.createAction("&Water Levels", self.dummyAction),
            "Parameter Estimation->Settings": self.createAction("&Settings", self.dummyAction),
            "Parameter Estimation->Run": self.createAction("&Run", self.dummyAction),
        }
        return actions

    def initMenuBar(self):
        menubar = self.menuBar()

        self.fileMenu = menubar.addMenu("&File")
        self.fileMenu.addAction(self.actions["File->New"])
        self.fileMenu.addAction(self.actions["File->Open"])
        self.fileMenu.addAction(self.actions["File->Save"])
        self.fileMenu.addAction(self.actions["File->Save As"])
        self.fileMenu.addAction(self.actions["File->Quit"])

        self.modelMenu = menubar.addMenu("&Model")
        self.modelMenu.addAction(self.actions["Model->Units"])
        self.modelMenu.addAction(self.actions["Model->Wells"])
        self.modelMenu.addAction(self.actions["Model->Aquifer Drawdown"])
        self.modelMenu.addAction(self.actions["Model->Well Loss"])
        self.modelMenu.addAction(self.actions["Model->Pumping Rates"])
        self.modelMenu.addSeparator()
        self.modelMenu.addAction(self.actions["Model->Run"])

        self.pestMenu = menubar.addMenu("&Parameter Estimation")
        self.pestMenu.addAction(self.actions["Parameter Estimation->Water Levels"])
        self.pestMenu.addAction(self.actions["Parameter Estimation->Settings"])
        self.pestMenu.addSeparator()
        self.pestMenu.addAction(self.actions["Parameter Estimation->Run"])

    def initUI(self):               
        self.statusBar()

        self.initMenuBar()
        self.setWindowTitle('AWFM')    
        self.showMaximized()

    def new(self):
        if self.okToProceed():
            self.model = awfm.core.Model()
            self.setDirty(True)
            self.setModelLoaded(True)

    def okToProceed(self):
        if self.isDirty:
            msgBox = QMessageBox()
            msgBox.setText("The current model has unsaved changes.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            ret = msgBox.exec()
            if ret == QMessageBox.Save:
                if self.save():  # AL: make sure self.save returns True on successful save
                    return True
                else:
                    return False
            elif ret == QMessageBox.Discard:
                return True
            elif ret == QMessageBox.Cancel:
                return False
            else:
                pass
        else:
            return True

    def open(self):
        if self.okToProceed:
            fileName = QFileDialog.getOpenFileName(self, 'Open Model')
            if fileName:
                self.model = awfm.core.io.open_model(fileName)
                self.saveFileName = fileName
                self.setModelLoaded(True)

    def quit(self):
        if self.okToProceed():
            qApp.quit()

    def save(self):
        if self.saveFileName is None:
            return self.saveAs()
        else:
            awfm.io.save_model(self.model, self.saveFileName)
            self.setDirty(False)
            return True

    def saveAs(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save Model As","","SQLite (*.db)", options=options)
        if fileName:
            self.saveFileName = fileName
            awfm.core.io.save_model(self.model, self.saveFileName)
            self.setDirty(False)
            return True
        else:
            return False

    def setDirty(self, is_dirty):
        self.isDirty = is_dirty
        self.actions["File->Save"].setEnabled(is_dirty)
        self.actions["File->Save As"].setEnabled(is_dirty)

    def setModelLoaded(self, model_is_loaded):
        self.modelMenu.setEnabled(model_is_loaded)
        self.pestMenu.setEnabled(model_is_loaded)
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = AWFMMainWindow()
    sys.exit(app.exec_())