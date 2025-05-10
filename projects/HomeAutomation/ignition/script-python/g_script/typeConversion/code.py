def ignDsToTableDict(ignDs):
	'''
	Convert ignition dataset and turn into tables dictionary that is recognizable by time-series chart / table props data.
	
    Args:
		ignDs (dataset): 
			Ignition dataset type or dataset datetype
	
    Returns
    	list: table dictionaries that is usable by time-series chart / table props data.
	'''
	rowCount = ignDs.getRowCount()
	columnNames = ignDs.getColumnNames()
	
	#force the value into list with dict in it. 
	#Ignition Table and Charts read rows first then have consistent columns.
	tableDict = []
	for idx in range(rowCount):
		columnsData = {}
		for columnName in columnNames:
			columnsData[columnName] = ignDs.getValueAt(idx, columnName)
		tableDict.append(columnsData)
	return tableDict