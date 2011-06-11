from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import os, logging, util, showquery
from imagemodel import ImageModel
import urllib2, re, string, time
from BeautifulSoup import BeautifulSoup

# the ImageModel table is a one-stop datasource for all images, so the iphone app can do a fast query by neighborhood for the next un-geotagged image
# the purpose of this cron job is to keep that table in sync with any image additions to the wiki site, and also provide a single datasource for fast 
#    lookups of ungeotagged images by neighborhood, which is unwieldy just using the wiki api
# this job takes a few steps:
# 1. back up current ImageModel to another table instance by date
# 2. if successful, drop oldest ImageModel table (keep last 2 weeks, 14?)
# 3. do a query on the mediawiki api and get a list of all images with metadata, like pageid and geotags
# 4. drop current ImageModel and recreate with this new data

class JobLinksEndpoint(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/html"
		self.runjobs()
		#self.saveimagedictionary()
		
	def runjobs(self):
		wikidomain = "http://beta.shapingsf-wiki.org/"
		page = urllib2.urlopen(wikidomain + "api.php?action=query&list=categorymembers&cmtitle=Category:Neighborhood/Geography&cmtype=subcat&cmlimit=100&format=xml")
		
		soup = BeautifulSoup(page)
		results = []

		for cm in soup.findAll('cm'):
			title = cm['title'][len('Category:'):]
			hood = string.replace(title," ","_") 
			apiurl = "<a href=\"http://foundsf-api.appspot.com/api/job?hood=" + hood + "\">http://foundsf-api.appspot.com/api/job?hood=" + hood + "</a><br/>"
			self.response.out.write(apiurl)
			
				
app = webapp.WSGIApplication([('/api/joblinks', JobLinksEndpoint)])

def main(): 
	run_wsgi_app(app)

if __name__ == "__main__": main()