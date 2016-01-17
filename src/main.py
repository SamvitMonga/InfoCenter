import sys
from PyQt4.QtGui import *
import json
import time
import threading
import urllib2

realTimeUrl = "http://realtimemap.grt.ca/Stop/GetStopInfo?stopId={stopID}&routeId={routeID}";

def updateTimes():
	f = urllib2.urlopen(realTimeUrl.format(stopID = '1165', routeID = '7')).read()
	timesDict = json.loads(f)
	numBuses = len(timesDict['stopTimes'])

def foo():
	print(time.ctime())
	threading.Timer(10,foo).start()

# Create an PyQT4 application object.
a = QApplication(sys.argv)       
 # The QWidget widget is the base class of all user interface objects in PyQt4.
w = QWidget()
 # Set window size. 
w.resize(320, 240)
 # Set window title  
w.setWindowTitle("Goon Command Center") 
# Show window
w.show()

sys.exit(a.exec_())
# updateTimes()
# foo()