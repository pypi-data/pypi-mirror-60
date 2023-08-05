# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, importlib, os, platform, os.path, configparser
from .utils import cnf
from PyQt5.QtCore import pyqtSignal, QObject
from .QtVersion import *
showVersions()


import pyqtgraph as pg

pf = platform.platform()
print (pf)	
if 'Windows' in pf:
	from . import diodeIV, editor, filterCircuit, induction, MPU6050, npnCEout, pendulumVelocity
	from . import plotIV, pnpCEout, pt100, RCtransient, RLCsteadystate, RLCtransient
	from . import RLtransient, rodPendulum, scope, soundBeats, soundFreqResp, soundVelocity
	from . import sr04dist, utils, logger, XYplot, i2cLogger, tof, advanced_logger

schoolExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow',"Voltage measurement"), ('2.1','measure-dc')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance measurement"), ('2.2','res-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Series"), ('2.2a','res-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistors in Parallel"), ('2.2b','res-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitance measurement"), ('2.3','cap-measure')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Series"), ('2.3a','cap-series')],
[QT_TRANSLATE_NOOP('MainWindow',"Capacitors in Parallel"), ('2.3b','cap-parallel')],
[QT_TRANSLATE_NOOP('MainWindow',"Resistance by Ohm's law"), ('2.4','res-compare')],
[QT_TRANSLATE_NOOP('MainWindow','Direct and Alternating Currents'), ('2.5','ac-dc')],
[QT_TRANSLATE_NOOP('MainWindow','AC mains pickup'), ('2.6','line-pickup')],
[QT_TRANSLATE_NOOP('MainWindow','Separating AC and DC'), ('2.7','acdc-separating')],
[QT_TRANSLATE_NOOP('MainWindow','Conducting Human body'), ('2.8','conducting-human')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Human body'), ('2.9','res-body')],
[QT_TRANSLATE_NOOP('MainWindow','Light Dependent Resistor'), ('2.10','ldr')],
[QT_TRANSLATE_NOOP('MainWindow','Lemon Cell'), ('2.11','lemon-cell')],
[QT_TRANSLATE_NOOP('MainWindow','Simple AC generator'), ('2.12','ac-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Transformer'), ('2.13','transformer')],
[QT_TRANSLATE_NOOP('MainWindow','Resistance of Water'), ('2.14','res-water')],
[QT_TRANSLATE_NOOP('MainWindow','Generating Sound'), ('2.15','sound-generator')],
[QT_TRANSLATE_NOOP('MainWindow','Digitizing Sound'), ('2.16','sound-capture')],
[QT_TRANSLATE_NOOP('MainWindow','Stroboscope'), ('2.17','stroboscope')],
]


testEquipment = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.0', 'scope')]
#[QT_TRANSLATE_NOOP('MainWindow','Monitor and Control'), 'mon-con']
]


electronicsExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Diode Characteristics'),('3.11','diodeIV')],
[QT_TRANSLATE_NOOP('MainWindow','NPN Output Characteristics'),('3.12','npnCEout')],
[QT_TRANSLATE_NOOP('MainWindow','PNP Output Characteristics'),'pnpCEout'],
#[QT_TRANSLATE_NOOP('MainWindow','AM and FM'), 'amfm']
]

electronicsExptsScope = [ 
[QT_TRANSLATE_NOOP('MainWindow','Oscilloscope'),('3.0', 'scope')],
[QT_TRANSLATE_NOOP('MainWindow','Halfwave Rectifier'),('3.1','halfwave')],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'),('3.2','fullwave')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clipping'),('3.3','clipping')],
[QT_TRANSLATE_NOOP('MainWindow','Diode Clamping'),('3.4','clamping')],
[QT_TRANSLATE_NOOP('MainWindow','IC555 Multivibrator'),('3.5','osc555')],
[QT_TRANSLATE_NOOP('MainWindow','Transistor Amplifier (CE)'),'npnCEamp'],
[QT_TRANSLATE_NOOP('MainWindow','Inverting Amplifier'),('3.6','opamp-inv')],
[QT_TRANSLATE_NOOP('MainWindow','Non-Inverting Amplifier'),('3.7','opamp-noninv')],
[QT_TRANSLATE_NOOP('MainWindow','Integrator using Op-Amp'),('3.8','opamp-int')],
[QT_TRANSLATE_NOOP('MainWindow','Logic Gates'),('3.9','logic-gates')],
[QT_TRANSLATE_NOOP('MainWindow','Clock Divider Circuit'),('3.10','clock-divider')]
]

electricalExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Plot I-V Curve'),'plotIV'],
[QT_TRANSLATE_NOOP('MainWindow','XY Plotting'),'XYplot'],
[QT_TRANSLATE_NOOP('MainWindow','RLC Steady state response'),('4.1','RLCsteadystate')],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient response'),('4.2','RCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient response'),('4.3','RLtransient')],
[QT_TRANSLATE_NOOP('MainWindow','RLC transient response'),('4.4','RLCtransient')],
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Filter Circuit'),('4.5','filterCircuit')],
[QT_TRANSLATE_NOOP('MainWindow','Electromagnetic Induction'),('4.7','induction')]
]

soundExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Frequency Response of Piezo Buzzer'),('5.1','soundFreqResp')],
[QT_TRANSLATE_NOOP('MainWindow','Velocity of Sound'), ('5.2','soundVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Sound beats'), ('5.3','soundBeats')]
]

mechanicsExpts = [
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum with Light barrier'), ('6.1','rodPendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Pendulum Wavefrorm'),('6.2','pendulumVelocity')],
[QT_TRANSLATE_NOOP('MainWindow','Driven Pendulum resonance'),('6.3','driven-pendulum')],
[QT_TRANSLATE_NOOP('MainWindow','Distance by HY-SRF04 Echo module'), ('6.4','sr04dist')],
[QT_TRANSLATE_NOOP('MainWindow','Gravity by Time of Flight'), 'tof']
]

otherExpts = [ 
[QT_TRANSLATE_NOOP('MainWindow','Temperatue, PT100 Sensor'), ('6.5','pt100')],
[QT_TRANSLATE_NOOP('MainWindow','Data Logger'), 'logger'],
[QT_TRANSLATE_NOOP('MainWindow','Advanced Data Logger'), 'advanced_logger']
]

modulesI2C = [ 
[QT_TRANSLATE_NOOP('MainWindow','Magnetic Hysterisis (MPU925x Sensor)'),'BHCurve'],
[QT_TRANSLATE_NOOP('MainWindow','Luminosity(TSL2561) Logger'),'lightsensorlogger'],
[QT_TRANSLATE_NOOP('MainWindow','MPU-6050 Acccn, Velocity and Temp'), 'MPU6050'],
[QT_TRANSLATE_NOOP('MainWindow','General Purpose I2C Sensors'), 'i2cLogger']
]

pythonCodes = [ 
[QT_TRANSLATE_NOOP('MainWindow','Read Inputs'),  'readInputs'],
[QT_TRANSLATE_NOOP('MainWindow','Set DC Voltages'), 'setVoltages'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Single Input'), 'capture1'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Two Inputs'), 'capture2'],
[QT_TRANSLATE_NOOP('MainWindow','Capture Four Inputs'), 'capture4'],
[QT_TRANSLATE_NOOP('MainWindow','Triangular Waveform'), 'triangularWave'],
[QT_TRANSLATE_NOOP('MainWindow','Arbitrary Waveform'), 'waveforms'],
[QT_TRANSLATE_NOOP('MainWindow','Waveform Table'), 'table'],
[QT_TRANSLATE_NOOP('MainWindow','RC Transient'), 'RCtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RL Transient'), 'RLtransient'],
[QT_TRANSLATE_NOOP('MainWindow','RC Integration'), 'RCintegration'],
[QT_TRANSLATE_NOOP('MainWindow','Clipping with Diode'), 'clipping'],
[QT_TRANSLATE_NOOP('MainWindow','Clamping with Diode'), 'clamping'],
[QT_TRANSLATE_NOOP('MainWindow','Fullwave Rectifier'), 'fullwave'],
[QT_TRANSLATE_NOOP('MainWindow','NPN Ib vs IC plot'), 'npnTransferChar'],
[QT_TRANSLATE_NOOP('MainWindow','Fourier Transform'), 'FourierTransform'],
[QT_TRANSLATE_NOOP('MainWindow','Rod Pendulum'), 'rodpend']
]

languages = ['fr_FR','en_IN', 'es_ES', 'ml_IN']


#---------------------------------------------------------------------
		
class helpWin(QWebView):
		
	def closeEvent(self, e):
		"""
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
		self.parent.uncheckHelpBox.emit()
		return
			
	def __init__(self, parent, name = '', lang="en"):
		"""
		Class for the help window
		:param parent: this is the main window
		:param name: a tuple (title, HTML file indication)
		name[1] can be either a simple string or another iterable. When it is
		a simple string, it means that the file to open is in htm/<name>.html;
		on the contrary, name[1] is a list of file names, without their
		.html suffix, to be searched in a list of directories; the first
		hit during the search defines the file to open.
		:param lang: the desired language
		"""
		QWebView.__init__(self)

		self.parent=parent
		self.lang=lang

		if type(name[1]) is str:
			fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html', name[1]+'.html')
		else:
			fn = self.foundFirstHelp(name[1])
		self.load(QUrl.fromLocalFile(fn))
		self.setWindowTitle(unicode(self.tr('Help: %s')) %name[0])
		self.setMaximumSize(QSize(500, 1200))
		self.show()
		screen = QDesktopWidget().screenGeometry()
		self.move(screen.width()-self.width()-20, screen.height()-self.height()-60)

	def foundFirstHelp(self, proposed_files):
		"""
		Check in sequence, a list of directories for a file to be found,
		which is in the iterable proposed_files; the first match is
		returned immediately
		:parm: proposed_files a sequence of file names without a suffix
		:return: the first occurence of a matching file, else None
		"""
		htmlFiles=[f+".html" for f in proposed_files]
		dirs = [
			os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ExpEYES17', 'UserManual', str(self.lang)[:2], 'rst', 'qt5HTML'), # development environment for restructured text files
			os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ExpEYES17', 'UserManual', str(self.lang), 'rst', 'qt5HTML'), # development environment for restructured text files (complete LANG code)
			os.path.join("/usr/share/eyes17/rst", str(self.lang)[:2]), # packaged environment, restructured text files
			os.path.join("/usr/share/eyes17/rst", str(self.lang)), # packaged environment, restructured text files (complete LANG code)
			"/usr/share/eyes17/html", # packaged environment, plain HTML files	
			os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html'), # development environment, plain HTML files (must be last to let /usr/share/eyes17/main.py find help files in rst/**/)
		]
		for directory in dirs:
			for f in htmlFiles:
				target=	os.path.join(directory,f)
				if os.path.exists(target):
					return target	
		return None

class MainWindow(QMainWindow):
	WIDTH = 950
	HEIGHT = 600
	expWidget = None
	expName = ''
	hlpName = ''
	hwin = None
	
	uncheckHelpBox = pyqtSignal()
	
	def closeEvent(self, e):
		if self.hwin != None:
			self.hwin.close()

	def __init__(self, lang):
		"""
		The constructor.
		:param lang: the autodetected language, which comes from shell variables
		"""
		QMainWindow.__init__(self)

		config = configparser.ConfigParser()
		config.read(cnf)
		try:
			self.translators = self.translate(config['ScreenTheme']['language'])
			self.lang = config['ScreenTheme']['language']
		except:
			self.translators = self.translate(lang)
			self.lang=lang
			
		self.uncheckHelpBox.connect(self.uncheckTheHelpBox)

	def uncheckTheHelpBox(self):
		"""
		unchecks the help checkbox
		"""
		self.helpCB.setChecked(False)
		return

	def init_UI(self):
		self.makeMenu()
		self.setMinimumSize(self.WIDTH-100, self.HEIGHT-50)
		self.resize(self.WIDTH,self.HEIGHT)
		self._x = 100
		self._y = 10
		palette = QPalette()								# background color
		palette.setColor(QPalette.Background, QColor(61,168,165)) #("#99ccff")) "#88bbcc"
		self.setPalette(palette)	

		self.helpCB = QCheckBox(self.tr('Enable PopUp Help Window'))
		self.helpCB.stateChanged.connect(self.showHelp)
		#self.helpCB.setStyleSheet('background-color: white')

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.addWidget(self.helpCB)
		
		self.callExpt(testEquipment[0])					# Start the scope by default
		self.screen = QDesktopWidget().screenGeometry()
		self.show()
		self.move(20, 20)
		
		

	def showHelp(self):
		if self.helpCB.isChecked() == True:
			if self.hwin == None:
				self.hwin = helpWin(self, (self.title,self.hlpName), self.lang)
			self.hwin.show()
		else:
			if self.hwin != None: self.hwin.hide()
	
	
	def scope_help(self,e):
		self.hlpName = e[1]
		if self.expName != 'scope':
			explib = importlib.import_module('scope')
			try:
				if self.expWidget != None:
					self.expWidget.timer.stop()     # Stop the timer loop of current widget			
				self.hwin = None
				self.expWidget= None 			    # Let python delete it
				w = explib.Expt(p) 
				self.setWindowTitle(e[0])
				self.setCentralWidget(w)
				self.expWidget = w
				self.expName = 'scope'
			except:
				self.expName = ''
				self.setWindowTitle(self.tr('Failed to load scope'))
		self.hwin = None
		self.title = e[0]
		self.showHelp()
	

	def callExpt(self, e):
		"""
		:parm: e lst with a title and a HTML file designation; when e[1]
		is not a string, then it is an iterable with possible HTML file names,
		and the last file name may also be a module name.
		"""	
		module_name =  e[1] if type(e[1]) is str else e[1][-1]
		explib = importlib.import_module(module_name)
		try:
			if self.expWidget != None:
				self.expWidget.timer.stop()     # Stop the timer loop of current widget			
			self.hwin = None
			self.expWidget= None 			    # Let python delete it
			w = explib.Expt(p) 
			self.setWindowTitle(self.tr(e[0]))
			self.setCentralWidget(w)
			self.expWidget = w
			self.expName = e[1]
			self.hlpName = e[1]
			self.title = e[0]
			self.showHelp()
		except Exception as err:
			print("Exception:", err)	
			self.expName = ''
			self.setWindowTitle(unicode(self.tr('Failed to load %s')) %e[0])
		return
		
	def runCode(self, e):
		if self.expName != 'editor':
			self.callExpt( ('Python Coding', 'editor'))
		self.expWidget.mycode = e[1]
		self.expWidget.update()

	def setConfig(self,section, key, value):
		"""
		Sets some part of eyes17's configuration
		@param section a section of the configuration file cnf, for
		example: 'ScreenTheme'
		@param key for example: 'Background'
		@param value the text to assign to the key, for example: 'dark'
		"""
		config = configparser.ConfigParser()
		config.read(cnf)
		config[section][key] = value
		with open(cnf,"w") as out: config.write(out)
		return
	
	def setWBG(self):
		"""
		sets a light background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'light')
		QMessageBox.warning(
			self,
			self.tr('No immediate application'),
			self.tr("Please restart the application to lighten the screen's background")
		)
		return
		
	def setBBG(self):
		"""
		sets a dark background for the scope's screen
		"""	
		self.setConfig('ScreenTheme', 'Background', 'dark')
		QMessageBox.warning(
			self,
			self.tr('No immediate application'),
			self.tr("Please restart the application to darken the screen's background.")
		)
		return
	
	def makeMenu(self):
		bar = self.menuBar()
		bar.clear() # reset all menu actions
		mb = bar.addMenu(self.tr("Device"))
		mb.addAction(self.tr('Reconnect'), self.reconnect)
		mb.addAction(self.tr('LightBackGround next time'), self.setWBG)
		mb.addAction(self.tr('DarkBackGround next time'), self.setBBG)
		sm = mb.addMenu(self.tr("Choose Language"))
		for e in languages:
			sm.addAction(e,  lambda item=e: self.setLanguage(item))	

		em = bar.addMenu(self.tr("School Expts"))
		for e in schoolExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.scope_help(item))	

		em = bar.addMenu(self.tr("Electronics"))
		for e in electronicsExptsScope:
			em.addAction(self.tr(e[0]),  lambda item=e: self.scope_help(item))	
			
		for e in electronicsExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	
		
		em = bar.addMenu(self.tr("Electrical"))
		for e in electricalExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Sound"))
		for e in soundExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Mechanics"))
		for e in mechanicsExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("Other Expts"))
		for e in otherExpts:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("I2C Modules"))
		for e in modulesI2C:
			em.addAction(self.tr(e[0]),  lambda item=e: self.callExpt(item))	

		em = bar.addMenu(self.tr("PythonCode"))
		for e in pythonCodes:
			em.addAction(self.tr(e[0]),  lambda item=e: self.runCode(item))	

	def setLanguage(self,l):
			self.setConfig('ScreenTheme', 'language', l)
			self.translators=self.translate(l)
			self.lang=l
			return

	def reconnect(self):
		global p
		try:
			p.H.disconnect()
		except:
			pass
		p=eyes.open()
		self.expWidget.p = p
		self.expWidget.msg('')
		if p != None: 
			if self.expName == 'scope':
				self.expWidget.recover()
		
	# translation stuff
	def translate(self, lang = None):
		global app,t,t1

		try:
			app.removeTranslator(t)
			app.removeTranslator(t1)
		except:
			pass

		if lang is None:
			lang=QLocale.system().name()
		t=QTranslator()
		t.load("lang/"+lang, os.path.dirname(__file__))
		app.installTranslator(t)
		t1=QTranslator()
		t1.load("qt_"+lang,
			QLibraryInfo.location(QLibraryInfo.TranslationsPath))
		app.installTranslator(t1)
		self.init_UI()
		self.uncheckHelpBox.emit()
		return t,t1

def run():
	# Program starts here
	global app,p
	from . eyes17 import eyes as eyes
	p = eyes.open()
	if p != None: 
		p.set_sine(1000)
		p.set_sqr1(-1)
		p.set_pv1(0)
		p.set_pv2(0)
		p.set_state(OD1=0)

	app = QApplication(sys.argv)
	# translation stuff
	lang=QLocale.system().name()
	t=QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QTranslator()
	t1.load("qt_"+lang,
		QLibraryInfo.location(QLibraryInfo.TranslationsPath))
	app.installTranslator(t1)

	mw = MainWindow(lang)
	sys.exit(app.exec_())

if __name__ == '__main__':
	run()
