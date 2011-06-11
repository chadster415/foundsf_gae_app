from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import os, logging, util, showquery
from imagemodel import ImageModel
import urllib2, re, string
from BeautifulSoup import BeautifulSoup

# the ImageModel table is a one-stop datasource for all images, so the iphone app can do a fast query by neighborhood for the next un-geotagged image
# the purpose of this cron job is to keep that table in sync with any image additions to the wiki site, and also provide a single datasource for fast 
#    lookups of ungeotagged images by neighborhood, which is unwieldy just using the wiki api
# this job takes a few steps:
# 1. back up current ImageModel to another table instance by date
# 2. if successful, drop oldest ImageModel table (keep last 2 weeks, 14?)
# 3. do a query on the mediawiki api and get a list of all images with metadata, like pageid and geotags
# 4. drop current ImageModel and recreate with this new data

class JobEndpoint(webapp.RequestHandler): 
	
	def get(self):
		#self.response.headers["Content-Type"] = "text/plain"
		
		self.imagedictionary = {}
		self.populateimagedictionary(util.getqsvalue('hood'))
		self.saveimagedictionary()
		
	def populateimagedictionary(self, hood):
		logging.info("Starting population")
		wikidomain = "http://beta.shapingsf-wiki.org/"
		#page = urllib2.urlopen(wikidomain + "api.php?action=query&list=categorymembers&cmtitle=Category:Neighborhood/Geography&cmtype=subcat&cmlimit=100&format=xml")
		#logging.info("first url: %sapi.php?action=query&list=categorymembers&cmtitle=Category:Neighborhood/Geography&cmtype=subcat&cmlimit=100&format=xml" % (wikidomain))

		#soup = BeautifulSoup(page)
		pageids = ""
		results = []

		# for cm in soup.findAll('cm'):
		# 			title = cm['title'][len('Category:'):]
		# 			apiurl = wikidomain + "api.php?action=query&list=categorymembers&cmtitle=Category:" + string.replace(title," ","_") + "&cmtype=pages&cmlimit=500&format=xml"
		# 			#logging.info("second url: %sapi.php?action=query&list=categorymembers&cmtitle=Category:%s&cmtype=pages&cmlimit=500&format=xml" % (wikidomain, string.replace(title," ","_") ))
		# 			categorypage = urllib2.urlopen(apiurl)
		# 			categorysoup = BeautifulSoup(categorypage)
		# 
		# 			#logging.info(categorysoup.findAll('cm'))
		# 			for cm2 in categorysoup.findAll('cm'):
		# 				pageid = cm2['pageid']
		# 				logging.info('appending %s, %s' % (title, pageid))
		# 				results.append((title,pageid))
		# 				logging.info(results)
		
		apiurl = wikidomain + "api.php?action=query&list=categorymembers&cmtitle=Category:" + hood + "&cmtype=pages&cmlimit=500&format=xml"
		#logging.info("second url: %sapi.php?action=query&list=categorymembers&cmtitle=Category:%s&cmtype=pages&cmlimit=500&format=xml" % (wikidomain, string.replace(title," ","_") ))
		categorypage = urllib2.urlopen(apiurl)
		categorysoup = BeautifulSoup(categorypage)

		#logging.info(categorysoup.findAll('cm'))
		for cm2 in categorysoup.findAll('cm'):
			pageid = cm2['pageid']
			#logging.info('appending %s, %s' % (title, pageid))
			results.append((hood,pageid))
			#logging.info(results)
	
		logging.info(results)
#		x=1

		while (len(results) > 0):
			
			pageidarray = []
			i = 0
			while (i < 50):
				if (len(results) > 0):
					pageid = (results.pop())[1]
					pageidarray.append(pageid)
				i = i + 1	
									
			imageurl = wikidomain + "api.php?action=query&pageids=" + "|".join(pageidarray) + "&prop=images&imlimit=500&format=xml"
			#logging.info("Third url: %sapi.php?action=query&pageids=%s&prop=images&cmlimit=2000&format=xml" % (wikidomain, pageid))
			logging.info("Opening url:" + imageurl)
			imagepage = urllib2.urlopen(imageurl)
			imagesoup = BeautifulSoup(imagepage)
			for image in imagesoup.findAll('im'):
				pageid = image.parent.parent['pageid']
				logging.info("adding: sub " + image['title'][5:] + " = " + pageid + ", " + hood)
				self.imagedictionary[image['title'][5:]] = (pageid, hood)  #pageid, district name		
			
		logging.info(self.imagedictionary)	
		
	def saveimagedictionary(self):
		logging.info("Starting saving")
		newimagecount = updatedimagecount = 0
		imagestosave = []
			
		for imagename in self.imagedictionary.keys():
			#logging.info("Working on %s" % (imagename))
			dbimage = util.getimage(imagename)
			wikiimage = self.imagedictionary[imagename]
			if (dbimage is not None):
				#logging.info("DbImage found, setting %s, %i, %s" % (imagename, wikiimage[0], wikiimage[1]))
				dbimage.pageid=int(wikiimage[0])
				dbimage.neighborhood=wikiimage[1]
				imagetosave = dbimage
				newimagecount = newimagecount + 1
			else:	
				#logging.info("DbImage NOT found, setting %s, %i, %s" % (imagename, wikiimage[0], wikiimage[1]))
				imagetosave = ImageModel(
					pageid=int(wikiimage[0]),
					imageurl=imagename,
					neighborhood=wikiimage[1],
					usernameupdated='WikiUser')
				updatedimagecount = updatedimagecount + 1 					
									
			imagestosave.append(imagetosave)	
					
		try:
			db.put(imagestosave)
		except Exception, err:
			logging.error(str(err))
			
		logging.info("New images saved: " + str(newimagecount))
		logging.info("Updated images saved: " + str(updatedimagecount))
				
app = webapp.WSGIApplication([('/api/job', JobEndpoint)])

def main(): 
	run_wsgi_app(app)

if __name__ == "__main__": main()			