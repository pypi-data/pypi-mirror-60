# the goal of this program is to combine all logs into one log file
#The code below works like this:
#a list is made that contains all the contents of a folder
#The list is then sorted so that the files that start with lower numbers are put at the front and files with higher numbers are put at the back
#The while loop then travels up the list, starting from the bottom and does the same thing for subfolders
#Once the date folder is entered, the files are read and written to output folder
import os

originalPath = r"/home/luke/Documents/logbook"
saveLocation = r"/home/luke/Documents"
outputFileLocation = "/home/luke/Documents" + "/output.txt"

def main():
    createFile()

    #I feel like I could put this in the makeFolderList function somehow
    yearFolders = os.listdir(originalPath)
    yearFolders.sort() #Sort in Ascending numeric order

    #Not sure if putting parameters here is the best practice but it seems like the only way it will work
    dateParameters = ["none"]
    monthParameters = [dateParameters]
    yearParameters = [originalPath, yearFolders, monthParameters]

    makeFolderList(*yearParameters)
    removeExtraLines()
    print("Logs combined")

def createFile():
    if os.path.exists(outputFileLocation): #If file output.txt exists, remove it. If it doesn't, create it
        os.remove(outputFileLocation)
    else:
        open(outputFileLocation, 'a').close()
        print("Output.txt created")

def makeList(ogPath, prevList, counter):
        nextPath = ogPath + "/" + prevList[counter]
        newList = os.listdir(nextPath)
        newList.sort()
        return newList, nextPath

def makeFolderList(lastPath, currentFolderList, nextParamList): #nextListName
    count = 0
    while count < len(currentFolderList):
        nextFolderList, currentPath = makeList(lastPath, currentFolderList, count)
        if nextParamList != "none":
            makeFolderList(currentPath, nextFolderList, *nextParamList)
        elif nextParamList == "none":
            addData(nextFolderList, currentPath)
        count = count + 1

def addData(entries, dateFolderPath):
    d = 0
    while d < len(entries):
        entryPath = dateFolderPath + "/" + entries[d]
        with open(entryPath) as input:
            dateLine = input.readline()
            contentLine = input.readline()
            with open(outputFileLocation, "a") as output:
                output.writelines(dateLine)
                output.writelines(contentLine)
                output.writelines("\n")
                output.writelines("\n")
        d = d + 1

def removeExtraLines():
    lastLine = 0
    currentLine = 0
    with open(outputFileLocation, "r") as output:
        lines = output.readlines()
    with open(outputFileLocation, "w") as output:
        #deletes content of output file
        output.seek(0)
        output.truncate()

        for line in lines:
            if line == "\n":
                currentLine = 1
            else:
                currentLine = 0

            if lastLine == 1 and currentLine == 1:
                print("line removed")
            else:
                output.write(line)

            lastLine = currentLine
            currentLine = 0
    output.close()

#Sample output format
#year


#month year

#day month year
#time-"entry content"
