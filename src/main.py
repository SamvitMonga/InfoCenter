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
busUpdateFreq = 10000
weatherUpdateFreq = 60000

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
        self.setMinimumSize(1280,720)
        
        self.createWidgets()
        self.updateBus()
        self.updateWeather()

    def createWidgets(self):
        bigFont = QFont("Calibri", 36, QFont.Bold)
        self.tempLabel = QLabel(time.ctime(), self)
        self.tempLabel.setAlignment(Qt.AlignCenter)
        self.tempLabel.resize(self.width(), 50)
        self.tempLabel.setFont(bigFont)

        self.statusLabel = QLabel('Last Updated: {0}'.format(time.ctime()), self)
        self.statusLabel.setAlignment(Qt.AlignRight)
        self.statusLabel.resize(self.width(), 10)

        # Bus timing layout
        # Top destination labels
        
        # School label
        schLabel = QLabel("School", self)
        schLabel.setAlignment(Qt.AlignCenter)
        pixMap = QPixmap('../res/school.png')
        schoolPixmap = pixMap.scaled(64,64, Qt.KeepAspectRatio)
        schLabel.setPixmap(schoolPixmap)

        # Gym label
        gymLabel = QLabel("Gym", self)
        gymLabel.setAlignment(Qt.AlignCenter)
        pixMap = QPixmap('../res/gym.png')
        gymPixmap = pixMap.scaled(64,64, Qt.KeepAspectRatio)
        gymLabel.setPixmap(gymPixmap)

        # Downtown label
        downtownLabel = QLabel("Downtown", self)
        downtownLabel.setAlignment(Qt.AlignCenter)
        pixMap = QPixmap('../res/downtown.png')
        dtnPixmap = pixMap.scaled(64,64, Qt.KeepAspectRatio)
        downtownLabel.setPixmap(dtnPixmap)

        # Test bus label (under school)
        # self.busLbl = QLabel(str(schoolTimes[0][0]) +  " minutes for " + str(schoolTimes[0][1]), self)
        # --------------------------------------------
        
        schBusLayout = QVBoxLayout()
        self.schTable = QTableWidget()
        
        schBusLayout.addWidget(schLabel)
        self.schTable = self.createTable()
        schBusLayout.addWidget(self.schTable)

        # --------------------------------------------

        gymBusLayout = QVBoxLayout()
        self.gymTable = QTableWidget()
        
        self.gymTable = self.createTable()

        gymBusLayout.addWidget(gymLabel)
        gymBusLayout.addWidget(self.gymTable)

        # --------------------------------------------
        
        dtnBusLayout = QVBoxLayout()
        self.dtnTable = QTableWidget()

        self.dtnTable = self.createTable()

        dtnBusLayout.addWidget(downtownLabel)
        dtnBusLayout.addWidget(self.dtnTable)

        # --------------------------------------------

        destLayout = QHBoxLayout()
        destLayout.addLayout(schBusLayout)
        destLayout.addLayout(gymBusLayout)
        destLayout.addLayout(dtnBusLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tempLabel)
        mainLayout.addLayout(destLayout)
        mainLayout.addWidget(self.statusLabel)

        # self.tempLabel = QLabel(time.ctime(), self)        

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def updateBus(self):
        try:
            logging.info('%s : Updating bus data', time.ctime())
            # fetchTimes()
            # self.schTable.clearContents()
            # update contents
            timeStr = time.strftime('%I:%M %p', time.localtime())
            self.statusLabel.setText('Last updated at {0}'.format(timeStr))

        finally:
            QTimer.singleShot(busUpdateFreq,self.updateBus)
   
    def updateWeather(self):
        try:
            logging.info('%s : Updating weather', time.ctime())
            timeStr = time.strftime('%I:%M %p', time.localtime())
            self.tempLabel.setText(timeStr)
            # fetchWeather()
        
        finally:
            QTimer.singleShot(weatherUpdateFreq, self.updateWeather)

    def createTable(self):
        table = QTableWidget(5, 2)
        
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        for row in range(0, 5):
            table.setItem(row, 0, QTableWidgetItem("Time"))
            table.setItem(row, 1, QTableWidgetItem("Name"))
        return table


# def fetchWeather():
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

def main():
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()