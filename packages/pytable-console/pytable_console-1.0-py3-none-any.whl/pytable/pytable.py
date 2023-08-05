import math
import json
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from tableError import TableError

class pytable:
    def __getNumberOfTabs(self, string):
        return math.ceil(len(str(string))/7)

    def __getNumberOfMaximumTabs(self, list):
        tabs = 0
        for item in list:
            if (self.__getNumberOfTabs(item) > tabs):
                tabs = self.__getNumberOfTabs(item)
        return tabs

    def __getColumnsMaximumTabs(self, tableValues):
        columnsMaximumTabs = []
        for currentColumnNumber in range(0, self.numCols):
            listOfValuesInColumn = []
            for currentRowNumber in range(0, self.numRows):
                listOfValuesInColumn.append(tableValues[currentRowNumber][currentColumnNumber])
            columnsMaximumTabs.append(self.__getNumberOfMaximumTabs(listOfValuesInColumn))
        return columnsMaximumTabs

    def __getRowTitlesMaximumTabs(self, rowNames):
        return self.__getNumberOfMaximumTabs(rowNames)

    def __getColumnTitlesMaximumTabs(self, colNames, columnsMaximumTabs):
        for columnNameNumber in range(0, self.numCols):
            if (self.__getNumberOfTabs(colNames[columnNameNumber]) > columnsMaximumTabs[columnNameNumber]):
                columnsMaximumTabs[columnNameNumber] = self.__getNumberOfTabs(colNames[columnNameNumber])
        return columnsMaximumTabs

    def displayRow(self, row, useTitles = True):

        self.__resetTableValues()

        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        if (self.isColNames and useTitles):
            colTitleString = ''
            for currentColumnNumber in range(0, self.numCols):
                numberOfTabs = self.__getNumberOfTabs(self.colNames[currentColumnNumber])
                colTitleString += self.colNames[currentColumnNumber] + (self.columnsMaximumTabs[currentColumnNumber] - numberOfTabs + 1) * "\t"
            if (self.isRowNames):
                print ("\t"*self.rowNameMaximumTabs + colTitleString)
            else:
                print (colTitleString)

        rowString = ""
        for currentColumnNumber in range(0, self.numCols):
            numberOfTabs = self.__getNumberOfTabs(self.tableValues[row][currentColumnNumber])
            rowString += str(self.tableValues[row][currentColumnNumber]) + (self.columnsMaximumTabs[currentColumnNumber] - numberOfTabs + 1) * "\t"

        if (self.isRowNames and useTitles):
            numberOfNameTabs = self.__getNumberOfTabs(self.rowNames[row])
            rowNameString = self.rowNames[row] + (self.rowNameMaximumTabs - numberOfNameTabs + 1) * "\t"
            print(rowNameString + rowString)
        else:
            print(rowString)

    def displayColumn(self, column, useTitles=True):

        self.__resetTableValues()

        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        if (self.isColNames and useTitles):
            colTitleString = ''
            numberOfTabs = self.__getNumberOfTabs(self.colNames[column])
            colTitleString += self.colNames[column] + (self.columnsMaximumTabs[column] - numberOfTabs + 1) * "\t"
            if (self.isRowNames and useTitles):
                print ("\t"*self.rowNameMaximumTabs + colTitleString)
            else:
                print (colTitleString)
        for currentRowNumber in range(0, self.numRows):
            rowString = ""
            numberOfTabs = self.__getNumberOfTabs(self.tableValues[currentRowNumber][column])
            rowString += str(self.tableValues[currentRowNumber][column]) + (self.columnsMaximumTabs[column] - numberOfTabs + 1) * "\t"

            if (self.isRowNames and useTitles):
                numberOfNameTabs = self.__getNumberOfTabs(self.rowNames[currentRowNumber])
                rowNameString = self.rowNames[currentRowNumber] + (self.rowNameMaximumTabs - numberOfNameTabs + 1) * "\t"
                print(rowNameString + rowString)
            else:
                print(rowString)

    def displayTable(self):

        self.__resetTableValues()

        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        if (self.isColNames):
            colTitleString = ''
            for currentColumnNumber in range(0, self.numCols):
                numberOfTabs = self.__getNumberOfTabs(self.colNames[currentColumnNumber])
                colTitleString += self.colNames[currentColumnNumber] + (self.columnsMaximumTabs[currentColumnNumber] - numberOfTabs + 1) * "\t"
            if (self.isRowNames):
                print ("\t"*self.rowNameMaximumTabs + colTitleString)
            else:
                print (colTitleString)
        for currentRowNumber in range(0, self.numRows):
            rowString = ""
            for currentColumnNumber in range(0, self.numCols):
                numberOfTabs = self.__getNumberOfTabs(self.tableValues[currentRowNumber][currentColumnNumber])
                rowString += str(self.tableValues[currentRowNumber][currentColumnNumber]) + (self.columnsMaximumTabs[currentColumnNumber] - numberOfTabs + 1) * "\t"

            if (self.isRowNames):
                numberOfNameTabs = self.__getNumberOfTabs(self.rowNames[currentRowNumber])
                rowNameString = self.rowNames[currentRowNumber] + (self.rowNameMaximumTabs - numberOfNameTabs + 1) * "\t"
                print(rowNameString + rowString)
            else:
                print(rowString)

    def getRow(self, rowNumber, useTitles=False):
        row = []
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        for cell in self.tableValues[rowNumber]:
            row.append(cell)
        if (useTitles):
            row.insert(0, self.rowNames[rowNumber])
        return row

    def getColumn(self, columnNumber, useTitles=False):
        column = []
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        for row in range(0, self.numRows):
            column.append(self.tableValues[row][columnNumber])
        if (useTitles):
            column.insert(0, self.colNames[columnNumber])
        return column

    def getCell(self, rowNumber, columnNumber):
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        return self.tableValues[rowNumber][columnNumber]

    def getRowTotal(self, rowNumber):
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        row = self.getRow(rowNumber)
        total = 0
        for number in row:
            total += number
        return total

    def getColumnTotal(self, columnNumber):
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        column = self.getColumn(columnNumber)
        total = 0
        for number in column:
            total += number
        return total

    def getGrandTotal(self):
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        total = 0
        for row in self.tableValues:
            for cell in row:
                total += cell
        return total

    def addRow(self, contentList, beforeRowNumber=-1, header=''):
        if (len(contentList) != self.numCols):
            raise TableError.RowLengthError
        self.numRows += 1
        if (beforeRowNumber == -1):
            self.tableValues.append(contentList)
            self.rowNames.append(header)
            return
        self.tableValues.insert(beforeRowNumber, contentList)
        self.rowNames.insert(beforeRowNumber, header)

    def addColumn(self, contentList, beforeColumnNumber=-1, header=''):
        if (len(contentList) != self.numRows):
            raise TableError.ColumnLengthError
        for row in range(0, self.numRows):
            if (beforeColumnNumber == -1):
                self.tableValues[row].append(contentList[row])
            else:
                self.tableValues[row].insert(beforeColumnNumber, contentList[row])
        if (beforeColumnNumber == -1):
            self.colNames.append(header)
        else:
            self.colNames.insert(beforeColumnNumber, header)
        self.numCols += 1

    def changeCell(self, row, column, value):
        self.tableValues[row][column] = value

    def getTableAsList(self):
        return self.tableValues

    def json(self, jsonIndent=4):
        if(self.numRows <= 0 or self.numCols <= 0):
            raise TableError.TableEmptyError
        return json.dumps(self.tableValues, indent=jsonIndent)

    def __checkTableLengths(self):
        self.numRows = len(self.tableValues)
        try:
            self.numCols = len(self.tableValues[0])
        except IndexError as e:
            self.numCols = 0

    def __verifyTabs(self):
        self.isRowNames = True if len(self.rowNames) == self.numRows else False
        self.isColNames = True if len(self.colNames) == self.numCols else False

        self.columnsMaximumTabs = self.__getColumnsMaximumTabs(self.tableValues)

        if (self.isRowNames):
            self.rowNameMaximumTabs = self.__getRowTitlesMaximumTabs(self.rowNames)

        if (self.isColNames):
            self.columnsAndNameMaximumTabs = self.__getColumnTitlesMaximumTabs(self.colNames, self.columnsMaximumTabs)

    def __resetTableValues(self):
        self.__checkTableLengths()
        self.__verifyTabs()

    def __init__(self, tableValues, rowNames=[], colNames=[]):
        self.tableValues = tableValues
        self.rowNames = rowNames
        self.colNames = colNames
        self.__resetTableValues()
