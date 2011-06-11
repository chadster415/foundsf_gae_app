import os, logging, pyfo, cgi
from usermodel import UserModel
from imagemodel import ImageModel

def getqsvalue(key, default=None):
	qs = cgi.parse_qs(os.environ["QUERY_STRING"])
	value = None
	
	try:
		value = qs[key][0]
	except KeyError:
		if (default is not None):
			value = default
		else:	
			logging.error('Request made to ' + os.environ["PATH_INFO"] + ' but no ' + key + ' param present')
			
	return value
	
def toxml(value):
	return pyfo.pyfo(value, pretty=True, prolog=True)	
					
def getuser(username):
	# get user details from datastore here
	return UserModel.gql("WHERE username=:1",username).get()
	
def getimage(imagename):
	# get image from datastore here
	return ImageModel.gql("WHERE imageurl=:1",imagename).get()	