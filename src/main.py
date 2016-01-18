import sys
# import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import json
import time
import threading
import urllib2
import logging
import pprint

realTimeUrl = "http://realtimemap.grt.ca/Stop/GetStopInfo?stopId={stopID}&routeId={routeID}"

schoolStop = '1123'   # 2514 for Columbia/Lester, 1123 for UW-DC (testing purposes)
schoolBus = ['200','9']  # 7 for Columbia/Lester, [200, 9] for UW-DC (testing purposes)
schoolData = {}
schoolTimes = []

gymStop = '2514'
gymBus = ['31', '92', '7']
gymData = {}
gymTimes = []


downtownStop = '2523'
downtownBus = ['7']
downtownData = {}
downtownTimes = []

class MainWindow(QMainWindow):

    def __init__(self, win_parent = None):
        QMainWindow.__init__(self, win_parent)
        self.setMinimumSize(400,185)
        self.createWidgets()

    def createWidgets(self):

        self.tempLabel = QLabel("Time and Weather", self)
        self.tempLabel.resize(self.width(),50)

        # Bus timing layout
        # Top destination labels
        self.schLabel = QLabel("School", self)
        self.schLabel.setAlignment(Qt.AlignCenter)
        self.schLabel.setStyleSheet("QLabel { color : blue; }")

        self.gymLabel = QLabel("Gym", self)
        self.gymLabel.setAlignment(Qt.AlignCenter)
        self.downtownLabel = QLabel("Downtown", self)
        self.downtownLabel.setAlignment(Qt.AlignCenter)

        # Test bus label (under school)
        self.busLbl = QLabel(str(schoolTimes[0][0]) +  " minutes for " + str(schoolTimes[0][1]), self)
        
        schBusLayout = QVBoxLayout()
        schBusLayout.addWidget(self.schLabel)
        schBusLayout.addWidget(self.busLbl)
        
        gymBusLayout = QVBoxLayout()
        gymBusLayout.addWidget(self.gymLabel)
        gymBusLayout.addWidget(self.busLbl)
        
        dtnBusLayout = QVBoxLayout()
        dtnBusLayout.addWidget(self.downtownLabel)
        dtnBusLayout.addWidget(self.busLbl)

        destLayout = QHBoxLayout()
        destLayout.addLayout(schBusLayout)
        destLayout.addLayout(gymBusLayout)
        destLayout.addLayout(dtnBusLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tempLabel)
        mainLayout.addLayout(destLayout)

        # self.tempLabel = QLabel(time.ctime(), self)        

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

def getKey(item):
    return item[1]

def clearTimes():
    global schoolData
    global gymData
    global downtownData
    global schoolTimes
    global gymTimes
    global downtownTimes

    schoolData = {
        'status':'success',
        'stopTimes':[]
    }

    gymData = {
        'status':'success',
        'stopTimes':[]
    }

    downtownData = {
        'status':'success',
        'stopTimes':[]
    }




def fetchTimes():
    global schoolData
    global gymData
    global downtownData

    global schoolTimes
    global gymTimes
    global downtownTimes

    clearTimes()
    logging.info('Cleared old data')
    
    for bus in schoolBus:
        f = urllib2.urlopen(realTimeUrl.format(stopID=schoolStop, routeID=bus)).read()
        recJson = json.loads(f)
        if recJson['status'] == 'success':
            updated = True
            schoolData['stopTimes'].extend(recJson['stopTimes'])
            logging.info('Fetched times for bus # %s', bus)
    
    buses = schoolData['stopTimes']
    for bus in buses:
        tupl = (bus['Minutes'], bus['HeadSign'])
        schoolTimes.append(tupl)
    schoolTimes = sorted(schoolTimes, key = getKey)

    for bus in gymBus:
        f = urllib2.urlopen(realTimeUrl.format(stopID=gymStop, routeID=bus)).read()
        recJson = json.loads(f)
        if recJson['status'] == 'success':
            updated = True
            gymData['stopTimes'].extend(recJson['stopTimes'])
            logging.info('Fetched times for bus # %s', bus)

    buses = gymData['stopTimes']
    for bus in buses:
        tupl = (bus['HeadSign'], bus['Minutes'])
        gymTimes.append(tupl)
    gymTimes = sorted(gymTimes, key = getKey)

    for bus in downtownBus:
        f = urllib2.urlopen(realTimeUrl.format(stopID=downtownStop, routeID=bus)).read()
        recJson = json.loads(f)
        if recJson['status'] == 'success':
            updated = True
            downtownData['stopTimes'].extend(recJson['stopTimes'])
            logging.info('Fetched times for bus # %s', bus)

    buses = downtownData['stopTimes']
    for bus in buses:
        tupl = (bus['HeadSign'], bus['Minutes'])
        downtownTimes.append(tupl)
    downtownTimes = sorted(downtownTimes, key = getKey)

    logging.info('Fetched %s buses for School', len(schoolData['stopTimes']))
    logging.info('Fetched %s buses for Gym', len(gymData['stopTimes']))
    logging.info('Fetched %s buses for Downtown', len(downtownData['stopTimes']))

# def update():
#     global updated
# 	logging.info('%s : Updating data', time.ctime())
#     fetchTimes()
#     if updated:
#         renderBusUpdate()

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    fetchTimes()
    # threading.Timer(10,foo).start()

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()

    sys.exit(app.exec_())
    # 
    # window = QWidget()
    # window.resize(320, 240)
    # window.setWindowTitle("Goon Command Center") 

    # schLabel = QLabel("School")
    # schLabel.resize(100,50)
    # schLabel.setText("School")

    # window.add(schLabel)

    # w.show()
    # sys.exit(a.exec_())


if __name__ == '__main__':
    main()