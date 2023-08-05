from pytable import pytable as pt

numberOfRows = input('Rows: ')
numberOfColumns = input('Columns: ')

tableValues = []
for x in range(0, int(numberOfRows)):
    tableValues.append([])
for row in tableValues:
    for y in range(0, int(numberOfColumns)):
        row.append(y)

titles = []
for x in range(0, int(numberOfColumns)):
    titles.append("e"*(x+1))

table = pt(tableValues, rowNames=['one','two','three','four','five'], colNames=['one','two','three','four','five'])
table.displayTable()
table.addColumn([4,5,6,7,8], header='new')
table.displayTable()
table.addRow([4,5,6,7,8,9], header='old')
table.displayTable()
table.changeCell(0,0,'asdfjkl;asfjkl;asdf')
table.displayTable()
