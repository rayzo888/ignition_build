'''
This scripts hosted methods to probe values type.
'''
from java.math import BigDecimal
from array import array
from com.inductiveautomation.ignition.common.script.adapters import PyDocumentObjectAdapter

def typeCheckForTagConfig(value):
	'''
	This method check the type of the value if it is boolean, float or string primarily to return
	results for tag configurations.
	
	Input Params:
		- value : 
			value you wanted to check. Will return None if this method is unable to check that value.
	
	Return:
		- 'Folder', 'Boolean', 'Float', 'String'
	'''
	if hasattr(value, "__iter__"):
		result = 'Folder'
	# Check type
	checkType = type(value)
	datatypeMap = {PyDocumentObjectAdapter: 'dict' ,array: 'array', bool:'Boolean', long: 'Float4', unicode: 'String', BigDecimal:'Float4'}
	try:
		result = datatypeMap[checkType]
		return result
	except:
		return result