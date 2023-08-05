'''
Code for studying newton's laws using sr04 sensor
Logs data from various sensors.
Author  : Jithin B.P, jithinbp@gmail.com
Date    : Sep-2019
License : GNU GPL version 3
'''
import sys

if sys.version_info.major==3:
	from PyQt5 import QtGui, QtCore, QtWidgets
else:
	from PyQt4 import QtGui, QtCore
	from PyQt4 import QtGui as QtWidgets

import time, utils, math, os.path, struct
from collections import OrderedDict

from layouts import ui_scope

from layouts.gauge import Gauge
import functools
from functools import partial
import time



from pyqtgraph.exporters import Exporter
from pyqtgraph.parametertree import Parameter
from pyqtgraph.Qt import QtGui, QtCore, QtSvg, USE_PYSIDE
from pyqtgraph import functions as fn
import pyqtgraph as pg

__all__ = ['PQG_ImageExporter']


class PQG_ImageExporter(Exporter):
    Name = "Working Image Exporter (PNG, TIF, JPG, ...)"
    allowCopy = True

    def __init__(self, item):
        Exporter.__init__(self, item)
        tr = self.getTargetRect()
        if isinstance(item, QtGui.QGraphicsItem):
            scene = item.scene()
        else:
            scene = item
        # scene.views()[0].backgroundBrush()
        bgbrush = pg.mkBrush('w')
        bg = bgbrush.color()
        if bgbrush.style() == QtCore.Qt.NoBrush:
            bg.setAlpha(0)

        self.params = Parameter(name='params', type='group', children=[
            {'name': 'width', 'type': 'int',
                'value': tr.width(), 'limits': (0, None)},
            {'name': 'height', 'type': 'int',
                'value': tr.height(), 'limits': (0, None)},
            {'name': 'antialias', 'type': 'bool', 'value': True},
            {'name': 'background', 'type': 'color', 'value': bg},
        ])
        self.params.param('width').sigValueChanged.connect(self.widthChanged)
        self.params.param('height').sigValueChanged.connect(self.heightChanged)

    def widthChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.height()) / sr.width()
        self.params.param('height').setValue(
            self.params['width'] * ar, blockSignal=self.heightChanged)

    def heightChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.width()) / sr.height()
        self.params.param('width').setValue(
            self.params['height'] * ar, blockSignal=self.widthChanged)

    def parameters(self):
        return self.params

    def export(self, fileName=None, toBytes=False, copy=False):
        if fileName is None and not toBytes and not copy:
            if USE_PYSIDE:
                filter = ["*."+str(f)
                          for f in QtGui.QImageWriter.supportedImageFormats()]
            else:
                filter = ["*."+bytes(f).decode('utf-8')
                          for f in QtGui.QImageWriter.supportedImageFormats()]
            preferred = ['*.png', '*.tif', '*.jpg']
            for p in preferred[::-1]:
                if p in filter:
                    filter.remove(p)
                    filter.insert(0, p)
            self.fileSaveDialog(filter=filter)
            return

        targetRect = QtCore.QRect(
            0, 0, self.params['width'], self.params['height'])
        sourceRect = self.getSourceRect()

        #self.png = QtGui.QImage(targetRect.size(), QtGui.QImage.Format_ARGB32)
        # self.png.fill(pyqtgraph.mkColor(self.params['background']))
        w, h = self.params['width'], self.params['height']
        if w == 0 or h == 0:
            raise Exception(
                "Cannot export image with size=0 (requested export size is %dx%d)" % (w, h))
        bg = np.empty((int(self.params['width']), int(
            self.params['height']), 4), dtype=np.ubyte)
        color = self.params['background']
        bg[:, :, 0] = color.blue()
        bg[:, :, 1] = color.green()
        bg[:, :, 2] = color.red()
        bg[:, :, 3] = color.alpha()
        self.png = fn.makeQImage(bg, alpha=True)

        # set resolution of image:
        origTargetRect = self.getTargetRect()
        resolutionScale = targetRect.width() / origTargetRect.width()
        #self.png.setDotsPerMeterX(self.png.dotsPerMeterX() * resolutionScale)
        #self.png.setDotsPerMeterY(self.png.dotsPerMeterY() * resolutionScale)

        painter = QtGui.QPainter(self.png)
        #dtr = painter.deviceTransform()
        try:
            self.setExportMode(True, {
                               'antialias': self.params['antialias'], 'background': self.params['background'], 'painter': painter, 'resolutionScale': resolutionScale})
            painter.setRenderHint(
                QtGui.QPainter.Antialiasing, self.params['antialias'])
            self.getScene().render(painter, QtCore.QRectF(
                targetRect), QtCore.QRectF(sourceRect))
        finally:
            self.setExportMode(False)
        painter.end()

        if copy:
            QtGui.QApplication.clipboard().setImage(self.png)
        elif toBytes:
            return self.png
        else:
            self.png.save(fileName)


PQG_ImageExporter.register()

import numpy as np
import math
import numpy.linalg

colors=['#00ff00','#ff0000','#ffff80',(10,255,255)]+[(50+np.random.randint(200),50+np.random.randint(200),150+np.random.randint(100)) for a in range(10)]

Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

############# MATHEMATICAL AND ANALYTICS ###############

#TODO

############# MATHEMATICAL AND ANALYTICS ###############

class task:
	def __init__(self,func):
		self.func = func
		self.args=None
		self.kwargs=None
		self.update = False
		
	def set(self,*args,**kwargs):
		self.args = args
		self.kwargs = kwargs
		self.update = True
	def run(self):
		self.func(*self.args,**self.kwargs)
		self.update = False

class communicationHandler(QtCore.QObject):
	sigStat = QtCore.pyqtSignal(str,bool)

	def __init__(self, **kwargs):
		super(self.__class__, self).__init__()
		self.p = kwargs.get('dev',None)

		self.tasks = OrderedDict()
		for a in ['set_sine']:
			self.tasks[a] = task(getattr(self.p,a))

	def update(self,func,args=[],kwargs={}):
		self.tasks[func].set(*args,**kwargs)

	def run(self):
		while 1:
			print(time.time(),self.tasks['set_sine'].update)

class Expt(QtWidgets.QMainWindow, ui_scope.Ui_MainWindow):
	sigExec = QtCore.pyqtSignal(str,list,dict)
	def __init__(self, parent=None,device=None):
		super(Expt, self).__init__(parent)
		self.setupUi(self)


		### Prepare the communication handler, and move it to a thread.
		self.CH = communicationHandler(dev=device)
		self.worker_thread = QtCore.QThread()
		self.CH.moveToThread(self.worker_thread)
		self.sigExec.connect(self.CH.update)

		self.worker_thread.start()
		self.worker_thread.setPriority(QtCore.QThread.HighPriority)



		#Define some keyboard shortcuts for ease of use
		self.shortcutActions={}
		self.shortcuts={" ":self.toggleRecord}
		for a in self.shortcuts:
			shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
			shortcut.activated.connect(self.shortcuts[a])
			self.shortcutActions[a] = shortcut


		self.T = 0
		self.start_time = time.time()
		self.points=0
		self.time = np.empty(300)
		self.pcurve_data = np.empty(300)
		self.vcurve_data = []
		self.acurve_data = []

		self.pcurve = self.graphPosition.plot(pen=colors[0])
		self.graphPosition.setRange(xRange=[0, 2],yRange=[-5, 5])

		#cross hair
		self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		self.graphPosition.addItem(self.vLine, ignoreBounds=True)
		self.graphPosition.addItem(self.hLine, ignoreBounds=True)
		self.graphPosition.setTitle('Pause acquisition to view derivates here',justify='left')
		self.resultslabel = self.graphPosition.plotItem.titleLabel
		self.proxy = pg.SignalProxy(self.graphPosition.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

		self.splitter_2.setSizes([500,100])

		self.gauges=OrderedDict()
		row = 1; col=1;
		self.analogs = {'A1':[-16,16],'A2':[-16,16],'A3':[-3,3],'SEN':[0,3.3],'AN8':[0,3.3]}
		for a in self.analogs:
			gauge = Gauge(self,a)
			gauge.setObjectName(a)
			gauge.set_MinValue(self.analogs[a][0])
			gauge.set_MaxValue(self.analogs[a][1])
			self.gaugeLayout.addWidget(gauge,row,col)
			col+= 1
			if col == 3:
				row += 1
				col = 1
			self.gauges[a] = gauge

		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(50)

	def set_sine(self,val):
		self.sigExec.emit('set_sine',[val],{})
		#self.tasks['set_sine'].set(val)

	def mouseMoved(self,evt):
		pos = evt[0]  ## using signal proxy turns original arguments into a tuple
		vb = self.graphPosition.plotItem.vb
		if vb.sceneBoundingRect().contains(pos):
			mousePoint = vb.mapSceneToView(pos)
			index = int(np.abs(self.time - mousePoint.x()).argmin()) #(np.abs(arr-val)).argmin()
			if index > 0 and index < len(self.vcurve_data):
				self.resultslabel.setText("<span style='font-size: 12pt'>x=%0.3f,   <span style='color: green'>P=%0.1f cm</span>,<span style='color: red'>V=%0.2f</span>,   <span style='color: yellow'>A=%0.2f</span>" % (mousePoint.x(), self.pcurve_data[index], self.vcurve_data[index], self.acurve_data[index]))
			self.vLine.setPos(mousePoint.x())
			self.hLine.setPos(mousePoint.y())


	def updateViews(self,plot):
			for a in plot.viewBoxes:
				a.setGeometry(plot.getViewBox().sceneBoundingRect())
				a.linkedViewChanged(plot.plotItem.vb, a.XAxis)

	def updateEverything(self):
		for a in self.analogs:
			#D = self.p.get_average_voltage(a)
			D = 1
			self.gauges[a].update_value(D)
		#for a in self.tasks:
		#	if self.tasks[a].update:
		#		self.tasks[a].run()
		#		break

		'''
		now = time.time()
		dt = now - self.lastTime
		self.lastTime = now
		if self.fps is None:
			self.fps = 1.0/dt
		else:
			s = np.clip(dt*3., 0, 1)
			self.fps = self.fps * (1-s) + (1.0/dt) * s
		'''
		#self.pcurve.setData(self.time[:self.points],self.pcurve_data[:self.points])

	def clearAll(self):
		self.T = 0
		self.start_time = time.time()
		self.points=0
		self.time = np.empty(300)
		self.pcurve_data = np.empty(300)
		self.vcurve_data = []
		self.acurve_data = []

		self.graphPosition.setRange(xRange=[-5, 0])
		self.pcurve.setPos(0, 0)

		for a in [self.pcurve,self.pcurve2,self.vcurve,self.acurve]:
			a.clear()

	def setRecord(self,val):
		self.rec = val
		if self.rec:
			self.clearAll()
			self.resultslabel.setText('Acquiring data...')
			self.splitter.setSizes([200,100])
		else:
			self.splitter.setSizes([100,200])
	def toggleRecord(self):
		if self.rec:
			self.recordBox.setChecked(False)
			self.setRecord(False)
			self.analysis()
		else:
			self.recordBox.setChecked(True)
			self.setRecord(True)

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QtWidgets.QApplication(sys.argv)

	# translation stuff
	lang=QtCore.QLocale.system().name()
	t=QtCore.QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QtCore.QTranslator()
	t1.load("qt_"+lang,
	        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
	app.installTranslator(t1)
	class dummydev:
		def sr04_distance(self):
			return np.random.random(1)
	mw = Expt(None,dev)
	mw.show()
	sys.exit(app.exec_())
	
