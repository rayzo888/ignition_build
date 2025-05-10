def convertHistTagPathsToNames(paths):
	names = []
	for path in paths:
		tagPath = path.toString().split(':/tag:')[-1]
		delimitedString = tagPath.split('/')
		joinedLast2SubString = '_'.join(delimitedString[-2:])
		names.append(joinedLast2SubString)
	return names