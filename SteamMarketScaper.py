#Version: 1.1
#Created by: Mark Nijjar (mark_nijjar@hotmail.com)

import re
import requests
import urllib
import datetime
import time
import os.path
import cPickle as pickle

#skins list url: http://counterstrike.wikia.com/wiki/Skins/List

DEBUG = True
SLEEP_TIME = 2

skinQuality = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
skinQualityAbv = ['FN', 'MW', 'FT', 'WW', 'BS']

skinColour = {'contraband': 'Brown',  'covert': 'Red', 'classified': 'Pink', 'restricted': 'Purple', 'mil-spec': 'Blue', 'industrial grade': 'Light-Blue', 'consumer grade': 'White',}
skinColourList = ['Brown', 'Red', 'Pink', 'Purple', 'Blue', 'Light-Blue', 'White']

allSkins = []
cases = {}

FNSkins = {}
MWSkins = {}
FTSkins = {}
WWSkins = {}
BSSkins = {}


curDir = os.path.abspath('')

class Currency():
    USD = str(1)
    CHF = str(4)
    R = str(7)
    KR = str(9)
    CAD = str(13)

currency = Currency.CAD
appID = str(730) #CS:GO application ID is 730


class skin():
    timeUpdated = str()
    url = str()
    case = str()
    name = str()
    weapon = str()
    quality = str()
    colour = str()
    statTrak = bool()
    volume = 0
    priceLow = 0.0
    priceMed = 0.0
    #Initialization function for creating skin data object
    #Weapon type [str], skinName [str], qualityValue [int], statTrak[bool]
    def __init__(self, case, weaponType, skinName, qualityValue, statTrak, colour):
        statTrakstr = str()
        #Define class variables
        self.statTrak = statTrak
        self.case = case
        self.quality = qualityValue
        self.name = skinName
        self.weapon = weaponType
        self.colour = skinColour[colour.lower()]
        #Get skin Quality text from Dictionary and convert it for URL
        self.quality = urllib.quote(skinQuality[qualityValue])
        if(self.statTrak):
            statTrakstr = "StatTrak%E2%84%A2%20"
        self.url = """http://steamcommunity.com/market/priceoverview/?currency="""+currency+"""&appid="""+appID+"""&market_hash_name="""\
                   +statTrakstr+self.weapon+"""%20%7C%20"""+urllib.quote(skinName)+"""%20"""+"%28"+self.quality+"%29"


    def parseJson(self, rJson):
        volume = 0
        priceMed = -1
        priceLow = -1
        #responseJson
        jsonKeys = rJson.keys()
        #Check that there are required # of keys/Data available
        if(rJson['success']):
            #Parse out data from JSON by key index [ignoring 'S$' prefix]
            try:
                volume = int(str(rJson['volume']))
            except:
                print 'No Volume Data Found!'
            try:
                priceMed = float(str(rJson['median_price'])[2:])
            except:
                print 'No priceMed Data Found!'
            try:
                priceLow = float(str(rJson['lowest_price'])[2:])
            except:
                print 'No priceLow Data Found!'
            return volume, priceLow, priceMed
        else:
            print "Error parsing data!"
            return 0,0,0

    def updateData(self):
        attempts = 1
        #fetch url data
        time.sleep(SLEEP_TIME)
        r = requests.get(self.url)
        while(r.text == "null" and attempts < 5):
            print "Null data page fetched, waiting 30 seconds cooldown.  Attempt " + str(attempts)
            time.sleep(30)
            r = requests.get(self.url)
            attempts += 1
        if(attempts > 4):
            print 'Too many attempts returned Null web page. Passing this skin.'
            print 'url: '+ self.url
        if(r.ok):
            self.volume, self.priceLow, self.priceMed = self.parseJson(r.json())
            if(self.volume == self.priceLow == self.priceMed == 0):
                print "No data collected from url:"
                print self.url+'\n'
                return False
            return True
        #Commented Below code is now handeled through parseSkins() function
        # parseSkins() will change quality of skin object and re-updating Data
        if(DEBUG):
            print "Error fetching page data!\n"
            print "url: "+self.url+'\n'


        #Update changes with current date time string
        self.timeUpdated = str(datetime.datetime.now())
        #print timeUpdated
        return

    def printData(self):
        print "[{0}]  {1}  {2}  ({3})  Low: {4}  Med: {5}  Vol: {6}".format(self.colour, self.weapon, self.name, urllib.unquote(self.quality), self.priceLow, self.priceMed, self.volume)
 
    def setQuality(self, qualityValue):
        statTrakstr = str()
        #Get skin Quality text from Dictionary and convert it for URL
        self.quality = urllib.quote(skinQuality[qualityValue])
        if(self.statTrak):
            statTrakstr = "StatTrak%E2%84%A2%20"
        self.url = """http://steamcommunity.com/market/priceoverview/?currency="""+currency+"""&appid="""+appID+"""&market_hash_name="""\
                   +statTrakstr+self.weapon+"""%20%7C%20"""+urllib.quote(self.name)+"""%20"""+"%28"+self.quality+"%29"

    def removeStatTrak(self):
        self.statTrak = False
        self.url = """http://steamcommunity.com/market/priceoverview/?currency="""+currency+"""&appid="""+appID+"""&market_hash_name="""\
                   +self.weapon+"""%20%7C%20"""+urllib.quote(self.name)+"""%20"""+"%28"+self.quality+"%29"


#This function reads all skins data from a file
# and returns a dictionary of all the cases and their skins
def parseSkins(fileName, skinQuality):
    allSkins = []
    cases = {}
    #emptySkin = skin('null', 'null', 0, False, '')
    #tempSkin = emptySkin
    f = open('CS GO skin list.txt', 'r')
    skinList = f.readlines() #Read file into a list
    for item in skinList:
        #Split text file into parts:
        #(Case)   (Weapon Type)   (Name)   (Quality)   (StatTrak Available)   (Qualities Avaialble)
        #[EXAMPLE:] Arms Deal   AUG   Wings   Mil-Spec   True   FN-MW
        if(item is not None):
            data = item.replace('\n', '').split('   ')
            if(data[0] not in cases):
                #If case not in dictionary, add new instance
                cases[data[0]] = []
                #If statTrack is available
            if(len(data) > 4):
                #tempSkin = skin(data[1], data[2], skinQuality, bool(data[4]), data[3].lower())
                tempSkin = skin(data[0], data[1], data[2], skinQuality, False, data[3].lower())
                #cases[data[0]].append(skin(data[1], data[2], 0, False, data[3].lower()))
            else:
                tempSkin = skin(data[0], data[1], data[2], skinQuality, False, data[3].lower())
            cases[data[0]].append(tempSkin)
            allSkins.append(tempSkin)
    return cases, allSkins


def updateSkinList(skinList, statTrak=False):
    qualityNum = skinQuality.index(urllib.unquote(skinList[1].quality))
    for skin in skinList:
        #if(not statTrak):
        #skin.removeStatTrak() #Removing StatTrak for first data set
        skin.setQuality(qualityNum)
        skin.updateData()
        skin.printData()

def printListData(skinList):
    for skin in skinList:
        skin.printData()


#Return list of all weapon skins in a list that are of 'colour'
def listColour(colour, skinList):
    tempList = []
    for i in skinList:
        if(i.colour == colour):
            tempList.append(i)
    return tempList


#findSkinsQuality() #Find FN-MW etc, available for all skins

def updateCases(cases, skinQuality):
    for case in cases.keys():
        print case + ': \n'
        updateSkinList(cases.get(case), skinQuality, False)

def splitSkinColour(allSkins):
    skinDict = {}
    skinDict['Brown'] = listColour('Brown', allSkins)
    skinDict['Red'] = listColour('Red', allSkins)          #Red    : 32
    skinDict['Pink'] = listColour('Pink', allSkins)        #Pink   : 59
    skinDict['Purple'] = listColour('Purple', allSkins)    #Purple : 103
    skinDict['Blue'] = listColour('Blue', allSkins)        #Blue   : 154
    skinDict['Light-Blue'] = listColour('Light-Blue', allSkins) #LBlue  : 86
    skinDict['White'] = listColour('White', allSkins)      #White  : 90
    return skinDict

def printCasesData(skinList):
    for case in skinList.keys():
        print '\n' + case + ': \n'
        printListData(skinList.get(case))

def loadFile(offsetPath):
    path = curDir + offsetPath
    inFile = open(path, 'rb')
    tempData = pickle.load(inFile)
    inFile.close()
    return tempData

def loadCase(skinDict):
    for key in cases:
        for caseSkin in cases.get(key): #Each skin in case
            for skin in skinDict[caseSkin.colour]: #Each skin in skinlist of Colour from Case
                if(skin.name == caseSkin.name):
                    print 'match'
                    caseSkin = skin
    return cases

def saveSkinData():
    dirs = ['\\Battle-Scarred\\skinData', '\\Well-Worn\\skinData', '\\Field-Tested\\skinData', '\\Minimal Wear\\skinData', '\\Factory New\\skinData']
    skins = [BSSkins, WWSkins, FTSkins, MWSkins, FNSkins]
    for skinSet in dirs:
        path = curDir + skinSet
        pFile = open(path, 'wb')
        pickle.dump(skins[dirs.index(skinSet)], pFile)
        pFile.close()

cases, allSkins = parseSkins('CS GO skins list.txt', 4) #Get all Factory New skin list
##FNSkins = splitSkinColour(allSkins)
##MWSkins, allSkins = parseSkins('CS GO skins list.txt', 1) #Get all Minimal Wear skin list
##MWSkins = splitSkinColour(allSkins)
##FTcases, allSkins = parseSkins('CS GO skins list.txt', 2) #Get all Field-Tested skin list
##FTSkins = splitSkinColour(allSkins)
##WWcases, allSkins = parseSkins('CS GO skins list.txt', 3) #Get all Well-Worn skin list
##WWSkins = splitSkinColour(allSkins)
##BScases, allSkins = parseSkins('CS GO skins list.txt', 4) #Get all Battle-Scarred skin list
##BSSkins = splitSkinColour(allSkins)

BSSkins = loadFile('\\Battle-Scarred\\skinData')
WWSkins = loadFile('\\Well-Worn\\skinData')
FTSkins = loadFile('\\Field-Tested\\skinData')
MWSkins = loadFile('\\Minimal Wear\\skinData')
FNSkins = loadFile('\\Factory New\\skinData')


#Pickle Template/Example:

#  path = curDir + '\\white\\Factory New\\'
#  pickleFile = open(path+'skinData.txt', 'wb') #Create file handler used for pickling
#  pickle.dump(skinDict['white'], pickleFile) #Dump object into pickle File

#  pickleFile.close()
#  inFile = open('pickle.txt', 'rb') #Picke file handler for loading pickled objects
#  newList = pickle.load(inFile)
#  inFile.close()




##
# FIXME: This function does not work properly due to the
#          datetime.datetime value's set being improper
##
def getUpdateAge(case):
    currentTime = datetime.datetime.now()
    oldestTime = -1
    avgTime = -1
    for skin in case:
        print skin.timeUpdated
        numList = re.findall('[0-9]+', skin.timeUpdated)
        if(len(skin.timeUpdated) > 5):
            print len(numList)
            timeDelta = currentTime - datetime.datetime(int(numList[0]), int(numList[1]), int(numList[2]), int(numList[3]), int(numList[4]), int(numList[5]), int(numList[6]) )
            print timeDelta
            return 0
            

##
# This function creates a list of the available colours inside a skinsList
# i.e : [White, Blue, Purple, Pink]
##
def getAvailableColours(skinsList):
    coloursAvailable = []
    skinColourList = splitSkinColour(skinsList)
    for colour in skinColour:
        curColour = skinColour.get(colour)
        if(len(skinColourList[curColour]) > 0): #White, Light-Blue etc..
            #There are skins avialable in this colour
            coloursAvailable.append(curColour)
    return coloursAvailable

###
# This function finds the price of the lowest avaiable quality for a skin
#    I.E If no Battle-Scarred price exists, check Well-Worn, etc.
#
###
def getLowestPriceSkin(skin):
    lowestPrice = 0
    lowest = BSSkins[skin.colour.lower()][BSSkins[skin.colour.lower()].index(skin)].priceLow
    if( lowest > 0 ):
        print "Lowest at [Battle-Scarred]  {}".format(lowest)
        return lowest
    lowest = WWSkins[skin.colour.lower()][WWSkins[skin.colour.lower()].index(skin)].priceLow
    if( lowest > 0 ):
        print "Lowest at [Well-Worn] {}".format(lowest)
        return lowest
    lowest = FTSkins[skin.colour.lower()][FTSkins[skin.colour.lower()].index(skin)].priceLow
    if( lowest > 0 ):
        print "Lowest at [Field-Tested] {}".format(lowest)
        return lowest
    lowest = MWSkins[skin.colour.lower()][MWSkins[skin.colour.lower()].index(skin)].priceLow
    if( lowest > 0 ):
        print "Lowest at [Minimal Wear] {}".format(lowest)
        return lowest
    lowest = FNSkins[skin.colour.lower()][FMSkins[skin.colour.lower()].index(skin)].priceLow
    if( lowest > 0 ):
        print "Lowest at [Factory New] {}".format(lowest)
        return lowest
    print "Error findling lowest."
    return -1


###
# This function finds the lowest available priceLow in the list of skins
#
###
def lowestPrice(skinList):
    lowest = -1
    for skin in skinList:
        if(skin.priceLow != 0):
            if(lowest == -1): #Deal with first lowest skin
                lowest = skin.priceLow
            if(skin.priceLow < lowest):
                lowest = skin.priceLow
            if(skin.priceMed < lowest):
                lowest = skin.priceMed
    return lowest

###
# This function finds the average priceLow of skins in list
#   that don't have value of 0.0
###
def avgListPrice(skinList):
    avgPrice = 0
    numSkins = 0
    skippedSkins = 0
    for skin in skinList:
        if(skin.priceLow != 0):
            numSkins += 1
            avgPrice += skin.priceLow
        else:
            #Skin Data not found, finding lowest available value
            #newLowest = getLowestPriceSkin(skin)
            #if(newLowest != 0):
            #    numSkins += 1
            #    avgPrice += newLowest
            skippedSkins += 1
    if(skippedSkins > 0):
        print "{} skins ignored.".format(skippedSkins)
    if(numSkins > 0):
        avgPrice = avgPrice/numSkins
        return avgPrice
    else:
        return -1



##
# This function checks for direct quality case profits
#
# I.E Check a Battle-Scarred Case if there are a set of whites
#       that can profit into a Light-Blue
##
def DCP(case, margin): #Check Direct Case Profit
    matchesFound = 0
    returnString = ''
    colourData = {}
    coloursAvailable = getAvailableColours(case)
    caseColour = splitSkinColour(case)
    for colour in caseColour:
        skinList = caseColour.get(colour)
        if(len(caseColour.get(colour)) > 0):
            #[Avg, Low]
            colourData[colour] = [avgListPrice(skinList), lowestPrice(skinList)]
            #print "[{0}]  Avg:{1}  Lowest:{2}".format(colour, colourData[colour][0], colourData[colour][1])
    for colour in range(len(skinColourList)-1):
        highColour = skinColourList[colour]
        lowColour = skinColourList[colour+1]
        if(highColour in colourData and lowColour in colourData):
            if(colourData[highColour][0] > 0 and colourData[lowColour][1] > 0):
                profit = (colourData[highColour][0]/1.15)
                cost = (colourData[lowColour][1]) #The multiple of 10 was added into profit
                if(profit-margin > cost*10):
                    returnString += "Found: [{0}] Avg: {1} from [{2}] Low: {3}\n".format(highColour, profit, lowColour, colourData[lowColour][1])
                    matchesFound += 1
    if(matchesFound > 0):
        return returnString
    else:
        return ''

##
#This function runs Direct Case Profit for each case
#    in the Skin set (example: FNSkins)
##
def allDCP(skinSet, margin):
    for case in skinSet.keys():
        output = DCP(skinSet[case], margin)
        if(output != ''):
            print case + ':'
            print output
