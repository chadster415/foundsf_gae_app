from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import util, logging, urllib2, config
from urllib import quote, unquote
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
			try:
				(success, pageid, imageurl, text, hood) = self.getimage(hood, username)
				a=('response',[('success',success),('pageid',pageid),('imageurl',imageurl),('imagetext',text),('neighborhood',hood)])
				self.response.out.write(util.toxml(a))
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))	
						
		elif (op == 'tag' and imageurl is not None and pageid is not None and latcoord is not None and longcoord is not None):
			try:
				success = self.tagimage(imageurl, pageid, latcoord, longcoord, hood, username)
				a=('response',[('success',success)])
				self.response.out.write(util.toxml(a))
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))	
						
		elif (op == 'ignore' and imageurl is not None and username is not None):
			try:
				success = self.ignoreimage(imageurl, username)
				a=('response',[('success',success)])
				self.response.out.write(util.toxml(a))	
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))
				
		#else:
			#self.response.out.write(util.toxml(('response',[('success',False)])))
			
	def getimage(self, hood, username):
		
		modelimage = self.getfirstuntaggedimage(username, hood)		
		if (modelimage != None):		
			logging.info("Got image %s", modelimage.imageurl)
			imageinfo = self.getwikiimageurl(modelimage)
			imageurl = ""
			
			if (imageinfo != None):	
				imageurl = imageinfo['url']		
				comment = self.getwikiimagecomment(modelimage, imageinfo)			
				logging.info("%s, %s, %s, %s", str(modelimage.pageid), imageurl, comment, hood)
				return (True, modelimage.pageid, imageurl, comment, hood)
			else:
				return (True, modelimage.pageid, modelimage.imageurl, "", hood)			
			
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

		imageurl = util.convertimageurl(imageurl)	

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
			
	def getfirstuntaggedimage(self, username, hood):
		user = util.getuser(username)
		modelimage = None
		
		# make a call to the imagemodel KV store, passing the hood desired, and getting back the imageid, pageid and image url of the first one that has no geo coords, and is not in the user's ignored list		
		dbhood = util.underscoredistricturl(hood)
		query = db.GqlQuery("SELECT * FROM ImageModel where latcoord = null and longcoord = null and neighborhood = :1 order by updatetime asc", dbhood)
		images = query.fetch(len(user.ignored_images) + 1) #get one more than the amount of items in the ignored images list, so we are guaranteed to have at least one left once the list is filtered
		for singleimage in images: # now return the first image that is not in the user's ignored images list
			if singleimage.imageurl not in user.ignored_images: 
				modelimage = singleimage
				break
			else:
				logging.info("Ignoring %s", singleimage.imageurl)
		
		return modelimage
		
	def getwikiimageurl(self, image):
		#now fire off a query to get the absolute wiki image url
		apiurl = config.domain + "api.php?action=query&titles=File:" + quote(image.imageurl) + "&prop=imageinfo&iilimit=50&iiprop=url&format=xml"
		logging.info("calling %s for imageurl", apiurl)
		imagepage = urllib2.urlopen(apiurl)
		imagesoup = BeautifulSoup(imagepage)
		ii = imagesoup.find('ii')
		return ii
		
	def getwikiimagecomment(self, modelimage, imageinfo):	
		apiurl = config.domain + "api.php?action=query&pageids=" + str(modelimage.pageid) + "&prop=revisions&rvprop=content&format=xml"
		logging.info("calling %s for comment", apiurl)
		captionpage = urllib2.urlopen(apiurl)
		captionsoup = BeautifulSoup(captionpage)
		rev = captionsoup.find('rev').string

		#loop through newlines of text until we find the image name, then take the next line, which is the comment
		caption = "Not found"
		linearray = rev.split("""

""")
		#logging.info("Length of array is %i", len(linearray))
		linecount = 0
		found = False
		while (found == False and linecount < len(linearray) - 1):
			line = linearray[linecount].lower()
			nextline = linearray[linecount + 1]
			imurl = modelimage.imageurl.lower()
								
			logging.info("Processing %s" % line)
			logging.info("Examining ||%s|| against ||%s||", line, imurl)
			
			#sometimes the imageurl is quoted in the api response and sometimes not, so check both, and make sure the next line is not an internal api thing
			if ((line.find(quote(imurl)) > -1 or line.find(imurl) > -1) and nextline.find("[[") == -1):
				logging.info("Image url found!! Setting caption to:")
				caption = nextline
				logging.info("Caption: %s", caption)
				found = True
			else:
				linecount = linecount + 1

		caption = caption.replace("'''","")
		caption = caption.replace("''","")
		caption = util.decode_htmlentities(caption)
		return caption	
						
			
chatapp = webapp.WSGIApplication([('/api/image', ImageEndpoint)])

def main(): 
	run_wsgi_app(chatapp)

if __name__ == "__main__": main()