import types	
def listTostr(liststr):
	if len(liststr) == 0:
		return ''
	value = "["
	for i in range(0,len(liststr)-1):
		temp = ''
		if isinstance(liststr[i],list):
			temp = listTostr(liststr[i])
			value  = value + temp
		elif isinstance(liststr[i],dict):
			temp = dictTostr(liststr[i])
			value = value + temp
		elif isinstance(liststr[i],int):
			value = value + str(liststr[i])
		else:
			value  = value + liststr[i]
		value = value + ','
	temp = ''
	i = len(liststr)-1
	if isinstance(liststr[i],list):
		temp = listTostr(liststr[i])
		value  = value + temp
	elif isinstance(liststr[i],dict):
		temp = dictTostr(liststr[i])
		value = value + temp
	elif isinstance(liststr[i],int):
		value = value + str(liststr[i])
	else:
		value  = value + liststr[i]
	value = value + "]"
	return value
	
def dictTostr(dictstr):
	value = "{"
	keys = dictstr.keys()
	if len(keys) == 0:
		return ''
	for i in range(0,len(keys)-1):
		temp = ''
		value = value + keys[i] + ":"
		if isinstance(dictstr[keys[i]],list):
			temp = listTostr(dictstr[keys[i]])
			value = value + temp
		elif isinstance(dictstr[keys[i]],dict):
			temp = dictTostr(dictstr[keys[i]])
			value = value + temp
		elif isinstance(dictstr[keys[i]],int):
			value = value + str(dictstr[keys[i]])
		else:
			value = value + dictstr[keys[i]]
		value = value + ","
	i = len(keys)-1
	temp = ''
	value = value + keys[i] + ":"
	if isinstance(dictstr[keys[i]],list):
		temp = listTostr(dictstr[keys[i]])
		value = value + temp
	elif isinstance(dictstr[keys[i]],dict):
		temp = dictTostr(dictstr[keys[i]])
		value = value + temp
	elif isinstance(dictstr[keys[i]],int):
		value = value + str(dictstr[keys[i]])
	else:
		value = value + dictstr[keys[i]]
	value = value + "}"
	return value

