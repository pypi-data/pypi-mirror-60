# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/camera_control.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CameraControl(object):
    def setupUi(self, CameraControl):
        CameraControl.setObjectName("CameraControl")
        CameraControl.resize(241, 332)
        CameraControl.setMinimumSize(QtCore.QSize(190, 110))
        self.verticalLayout = QtWidgets.QVBoxLayout(CameraControl)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.roiFpsLabel = QtWidgets.QLabel(CameraControl)
        self.roiFpsLabel.setObjectName("roiFpsLabel")
        self.horizontalLayout_2.addWidget(self.roiFpsLabel)
        self.roiFpsSpinBox = QtWidgets.QSpinBox(CameraControl)
        self.roiFpsSpinBox.setMinimum(1)
        self.roiFpsSpinBox.setMaximum(150)
        self.roiFpsSpinBox.setProperty("value", 40)
        self.roiFpsSpinBox.setObjectName("roiFpsSpinBox")
        self.horizontalLayout_2.addWidget(self.roiFpsSpinBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.bufferSizeLabel = QtWidgets.QLabel(CameraControl)
        self.bufferSizeLabel.setObjectName("bufferSizeLabel")
        self.horizontalLayout_3.addWidget(self.bufferSizeLabel)
        self.bufferSizeSpinBox = QtWidgets.QSpinBox(CameraControl)
        self.bufferSizeSpinBox.setReadOnly(False)
        self.bufferSizeSpinBox.setMinimum(128)
        self.bufferSizeSpinBox.setMaximum(4096)
        self.bufferSizeSpinBox.setProperty("value", 1024)
        self.bufferSizeSpinBox.setObjectName("bufferSizeSpinBox")
        self.horizontalLayout_3.addWidget(self.bufferSizeSpinBox)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.startStopButton = QtWidgets.QPushButton(CameraControl)
        self.startStopButton.setCheckable(True)
        self.startStopButton.setObjectName("startStopButton")
        self.verticalLayout.addWidget(self.startStopButton)
        self.acquireFramesButton = QtWidgets.QPushButton(CameraControl)
        self.acquireFramesButton.setEnabled(False)
        self.acquireFramesButton.setCheckable(True)
        self.acquireFramesButton.setObjectName("acquireFramesButton")
        self.verticalLayout.addWidget(self.acquireFramesButton)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.acquireRoiCheckBox = QtWidgets.QCheckBox(CameraControl)
        self.acquireRoiCheckBox.setEnabled(False)
        self.acquireRoiCheckBox.setObjectName("acquireRoiCheckBox")
        self.horizontalLayout.addWidget(self.acquireRoiCheckBox)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.showFramesCheckBox = QtWidgets.QCheckBox(CameraControl)
        self.showFramesCheckBox.setChecked(True)
        self.showFramesCheckBox.setObjectName("showFramesCheckBox")
        self.horizontalLayout_4.addWidget(self.showFramesCheckBox)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem8)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem9)

        self.retranslateUi(CameraControl)
        QtCore.QMetaObject.connectSlotsByName(CameraControl)

    def retranslateUi(self, CameraControl):
        _translate = QtCore.QCoreApplication.translate
        CameraControl.setWindowTitle(_translate("CameraControl", "Form"))
        self.roiFpsLabel.setText(_translate("CameraControl", "ROI FPS:"))
        self.bufferSizeLabel.setText(_translate("CameraControl", "Buffer Size:"))
        self.startStopButton.setText(_translate("CameraControl", "Start Camera"))
        self.acquireFramesButton.setText(_translate("CameraControl", "Start Acquire Frames"))
        self.acquireRoiCheckBox.setText(_translate("CameraControl", "Acquire ROI"))
        self.showFramesCheckBox.setText(_translate("CameraControl", "Show Frames"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CameraControl = QtWidgets.QWidget()
    ui = Ui_CameraControl()
    ui.setupUi(CameraControl)
    CameraControl.show()
    sys.exit(app.exec_())
