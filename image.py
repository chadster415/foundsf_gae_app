from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import util, logging, string, urllib2
from urllib import quote
from imagemodel import ImageModel
from usermodel import UserModel
from BeautifulSoup import BeautifulSoup

class ImageEndpoint(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/xml"
		op = util.getqsvalue('op')
		imageurl = util.getqsvalue('imageurl')
		hood = util.getqsvalue('hood', 'Mission')
		pageid = util.getqsvalue('pageid')
		latcoord = util.getqsvalue('latcoord')
		longcoord = util.getqsvalue('longcoord')
		username = util.getqsvalue('username', 'Anonymous')
		success = None
		
		if (op == 'get'):
			(success, pageid, imageurl, text, hood) = self.getimage(hood, username)
			a=('response',[('success',success),('pageid',pageid),('imageurl',imageurl),('imagetext',text),('neighborhood',hood)])
			self.response.out.write(util.toxml(a))
						
		elif (op == 'tag' and imageurl is not None and pageid is not None and latcoord is not None and longcoord is not None):
			success = self.tagimage(imageurl, pageid, latcoord, longcoord, hood, username)
			a=('response',[('success',success)])
			self.response.out.write(util.toxml(a))
			
		elif (op == 'ignore' and imageurl is not None and username is not None):
			success = self.ignoreimage(imageurl, username)
			a=('response',[('success',success)])
			self.response.out.write(util.toxml(a))	
	
	def getimage(self, hood, username):
		user = util.getuser(username)
		image = None
		
		# make a call to the imagemodel KV store, passing the hood desired, and getting back the imageid, pageid and image url of the first one that has no geo coords, and is not in the user's ignored list
		dbhood = string.replace(hood, " ", "_")
		query = db.GqlQuery("SELECT * FROM ImageModel where latcoord = null and longcoord = null and neighborhood = :1 order by updatetime asc", dbhood)
		images = query.fetch(len(user.ignored_images) + 1) #get one more than the amount of items in the ignored images list, so we are guaranteed to have at least one left once the list is filtered
		for singleimage in images: # now return the first image that is not in the user's ignored images list
			if singleimage.imageurl not in user.ignored_images: 
				image = singleimage
				break
		
		if (image != None):
		
			logging.info("Got image %s", image.imageurl)
		
			#TODO: what if image is null??
		
			#now fire off this example of a query to get the absolute wiki url
			#http://beta.shapingsf-wiki.org/api.php?action=query&titles=File:Stepstotwinpeaks.gif&prop=imageinfo&iilimit=50&iiprop=url
			wikidomain = "http://beta.shapingsf-wiki.org/"
			apiurl = wikidomain + "api.php?action=query&titles=File:" + quote(image.imageurl) + "&prop=imageinfo&iilimit=50&iiprop=url&format=xml"
			logging.info("calling %s for imageurl", apiurl)
			imagepage = urllib2.urlopen(apiurl)
			imagesoup = BeautifulSoup(imagepage)
			ii = imagesoup.find('ii')		
			imageurl = ii['url']
		
			#now get the comment
			caption = ""
			apiurl = wikidomain + "api.php?action=query&pageids=" + str(image.pageid) + "&prop=revisions&rvprop=content&format=xml"
			logging.info("calling %s for comment", apiurl)
			captionpage = urllib2.urlopen(apiurl)
			captionsoup = BeautifulSoup(captionpage)
			rev = captionsoup.find('rev').string
			#logging.info("rev is: %s", rev)
		
			#loop through newlines of text until we find the image name, then take the next line, which is the comment
			caption = "Not found"
			linearray = rev.split("""

	""")
			#logging.info("Length of array is %i", len(linearray))
			linecount = 0
			found = False
			while (found == False and linecount < len(linearray) - 1):
			#    print("Processing %s" % (linearray[linecount]))
				#logging.info("Examining ||%s|| against ||%s||", linearray[linecount], image.imageurl)
				if (linearray[linecount].find(image.imageurl) > -1 and linearray[linecount + 1].find("[[") == -1):
					logging.info("Found!! Setting caption to:")
					caption = linearray[linecount + 1]
					logging.info("Caption: %s", caption)
					found = True
				else:
					linecount = linecount + 1

			caption = caption.replace("'","")	
		
			logging.info("%s, %s, %s, %s", str(image.pageid), imageurl, caption, hood)
			return (True, image.pageid, imageurl, caption, hood)
		else: # image == None
			return (False, "000", "", "", hood)
			
		
	def tagimage(self, imageurl, pageid, latcoord, longcoord, hood, username):
		imageurl = util.convertimageurl(imageurl)	
		query = db.GqlQuery("SELECT * FROM ImageModel where imageurl = :1", imageurl)
		image = query.get()
		
		if image is None:
			image = ImageModel(usernameupdated=username, imageurl=imageurl, pageid=int(pageid), latcoord=latcoord, longcoord=longcoord, neighborhood=hood)
		else:
			image.usernameupdated = username
			image.imageurl = imageurl
			image.pageid = int(pageid)
			image.latcoord = latcoord
			image.longcoord = longcoord
			image.neighborhood = hood	
		
		try:
			image.put()
			user = util.getuser(username)
			if (user is not None):
				user.count = user.count + 1
			else:
				user = UserModel(username=username, count=1)
					
			user.put()
			return True
		except Exception, err:
			logging.error(str(err))
			return False
			
	def ignoreimage(self, imageurl, username):
		logging.info("imageurl is going in as: %s", imageurl)
		imageurl = util.convertimageurl(imageurl)	
		logging.info("imageurl is coming out as: %s", imageurl)

		try:
			user = util.getuser(username)
			if (user is not None):
				user.count = user.count + 1
			else:
				user = UserModel(username=username, count=1)

			user.ignored_images.append(imageurl)
			user.put()
			return True
		except Exception, err:
			logging.error(str(err))
			return False		
			
chatapp = webapp.WSGIApplication([('/api/image', ImageEndpoint)])

def main(): 
	run_wsgi_app(chatapp)

if __name__ == "__main__": main()