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
busUpdateFreq = 30000
weatherUpdateFreq = 120000

schoolStop = '2514'   # 2514 for Columbia/Lester, 1123 for UW-DC (testing purposes)
schoolBus = ['7']  # 7 for Columbia/Lester, [200, 9] for UW-DC (testing purposes)
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
        self.minFont = QFont("Calibri", 24)
        self.nameFont = QFont("Calibri", 24)

        self.tempLabel = QLabel(time.ctime(), self)
        self.tempLabel.setAlignment(Qt.AlignCenter)
        self.tempLabel.resize(self.width(), 100)
        self.tempLabel.setFont(bigFont)

        self.statusLabel = QLabel('Last Updated: {0}'.format(time.ctime()), self)
        self.statusLabel.setAlignment(Qt.AlignRight)
        self.statusLabel.resize(self.width(), 10)

        # Bus timing layout
        
        # Top labels
        schLabel = self.createImgLabel('School', '../res/school.png')
        gymLabel = self.createImgLabel('Gym', '../res/gym.png')
        dtnLabel = self.createImgLabel('Downtown', '../res/downtown.png')

        # --------------------------------------------
        
        schBusLayout = QVBoxLayout()
        self.schTable = QTableWidget()
        
        schBusLayout.addWidget(schLabel)
        self.schTable = self.createTable()
        schBusLayout.addWidget(self.schTable)

        # --------------------------------------------

        gymBusLayout = QVBoxLayout()
        self.gymTable = QTableWidget()

        gymBusLayout.addWidget(gymLabel)
        self.gymTable = self.createTable()
        gymBusLayout.addWidget(self.gymTable)

        # --------------------------------------------
        
        dtnBusLayout = QVBoxLayout()
        self.dtnTable = QTableWidget()

        dtnBusLayout.addWidget(dtnLabel)
        self.dtnTable = self.createTable()
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

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
    
    def createTable(self):
        table = QTableWidget(5, 2)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setShowGrid(False)
        for row in range(0, 5):
            table.setItem(row, 0, QTableWidgetItem("Time"))
            table.setItem(row, 1, QTableWidgetItem("Name"))
        return table

    def createTableItem(self, name, font):
        item = QTableWidgetItem(name)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignVCenter)
        # item.setTextAlignment(Qt.AlignHCenter)
        item.setFlags(Qt.ItemIsEnabled)
        return item

    def updateTable(self, table, times):
        table.clearContents()

        for row in range (0, len(times)):
            minutes = self.createTableItem(str(times[row][0]) + ' min', self.minFont)
            name = self.createTableItem(str(times[row][1]), self.nameFont)

            table.setItem(row, 0, minutes)
            table.setItem(row, 1, name)

    def createImgLabel(self, label, path):
        imgLabel = QLabel(label, self)
        imgLabel.setAlignment(Qt.AlignCenter)
        pixMap = QPixmap(path)
        scaledPixmap = pixMap.scaled(64,64, Qt.KeepAspectRatio)
        imgLabel.setPixmap(scaledPixmap)
        return imgLabel

    def updateBus(self):
        try:
            logging.info('%s : Updating bus data', time.ctime())
            fetchTimes()
            self.updateTable(self.schTable, schoolTimes)
            self.updateTable(self.gymTable, gymTimes)
            print (downtownTimes)
            self.updateTable(self.dtnTable, downtownTimes)
            
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

    schoolTimes = []
    gymTimes = []
    downtownTimes = []

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
        tupl = (bus['Minutes'], bus['HeadSign'])
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
        tupl = (bus['Minutes'], bus['HeadSign'])
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