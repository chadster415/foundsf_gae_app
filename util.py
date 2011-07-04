import os, logging, pyfo, cgi, re, string
from usermodel import UserModel
from imagemodel import ImageModel
from htmlentitydefs import name2codepoint as n2cp

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
	
def convertimageurl(imageurl):
	if (imageurl.find("ttp://") > 0): #get rid of domains and dirs, only keep image name
		imageurl = imageurl.split("/")[-1]
		imageurl = imageurl.replace("_"," ") # for some reason, the url is stored on wikimedia in 2 diff formats, in one place with spaces, in another with _'s. The db should only know about the one with spaces
	return imageurl	
	
def underscoredistricturl(url):
	return string.replace(url, " ", "_")	
	
def substitute_entity(match):
	ent = match.group(2)
	if match.group(1) == "#":
		return unichr(int(ent))
	else:
		cp = n2cp.get(ent)

		if cp:
			return unichr(cp)
		else:
			return match.group()

def decode_htmlentities(string):
	entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
	return entity_re.subn(substitute_entity, string)[0]		