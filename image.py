from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import util, logging, string, urllib2
from imagemodel import ImageModel
from usermodel import UserModel
from BeautifulSoup import BeautifulSoup

class ImageEndpoint(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/xml"
		op = util.getqsvalue('op')
		hood = util.getqsvalue('hood', 'Mission')
		imageid = util.getqsvalue('imageid')
		pageid = util.getqsvalue('pageid')
		latcoord = util.getqsvalue('latcoord')
		longcoord = util.getqsvalue('longcoord')
		username = util.getqsvalue('username', 'Anonymous')
		success = None
		
		if (op == 'get'):
			(imageid, pageid, imageurl, text, hood) = self.getimage(hood)
			a=('response',[('imageid',imageid),('pageid',pageid),('imageurl',imageurl),('imagetext',text),('neighborhood',hood)])
			self.response.out.write(util.toxml(a))
						
		elif (op == 'tag' and imageid is not None and pageid is not None and latcoord is not None and longcoord is not None):
			success = self.tagimage(imageid, pageid, latcoord, longcoord, hood, username)
			a=('response',[('success',success)])
			self.response.out.write(util.toxml(a))
	
	def getimage(self, hood):
		# make a call to the imagemodel KV store, passing the hood desired, and getting back the imageid, pageid and image url of the first one that has no geo coords
		dbhood = string.replace(hood, " ", "_")
		query = db.GqlQuery("SELECT * FROM ImageModel where latcoord = null and longcoord = null and neighborhood = :1 order by updatetime asc", dbhood)
		image = query.get()
		
		logging.info("Got image %s", str(image))
		
		#TODO: what if image is null??
		
		#now fire off this example of a query to get the absolute wiki url
		#http://beta.shapingsf-wiki.org/api.php?action=query&titles=File:Stepstotwinpeaks.gif&prop=imageinfo&iilimit=50&iiprop=url
		wikidomain = "http://beta.shapingsf-wiki.org/"
		apiurl = wikidomain + "api.php?action=query&titles=File:" + image.imageurl + "&prop=imageinfo&iilimit=50&iiprop=url&format=xml"
		logging.info("calling %s for imageurl", apiurl)
		imagepage = urllib2.urlopen(apiurl)
		imagesoup = BeautifulSoup(imagepage)
		ii = imagesoup.find('ii')		
		imageurl = ii['url']
		
		logging.info("%s, 999, %s,Text, %s", str(image.pageid), imageurl, hood)
		return (image.pageid, 999, imageurl, 'Text', hood)
		
		
		# if (hood == 'Bayview/Hunter''s Point'):
		# 	return (999,998,'http://www.foundsf.org/images/2/2c/Bayvwhp%24view-north-from-hp.jpg','Text',hood)
		# elif (hood == 'Bernal Heights'):
		# 	return (999,998,'http://www.foundsf.org/images/6/6a/Mrs-williams-and-cow_300dpi.jpg','Text',hood)
		# elif (hood == 'Castro'):
		# 	return (999,998,'http://www.foundsf.org/images/9/92/Castro1%24castro-street-s-1915.jpg','18th and Castro looking south, July 12, 1915.',hood)
		# elif (hood == 'Chinatown'):
		# 	return (999,998,'http://www.foundsf.org/images/c/ca/Chinatwn%24nationalist-supporters-1910s.jpg','Nationalist Demonstration in Chinatown, c. 1911',hood)
		# elif (hood == 'Civic Center'):
		# 	return (999,998,'http://www.foundsf.org/images/8/8c/Crystal_palace_AAC-6908.jpg','Text',hood)
		# elif (hood == 'Diamond Heights'):
		# 	return (999,998,'http://www.foundsf.org/images/8/89/Glenpark%24goldmine-hill-1940.jpg','Text',hood)
		# elif (hood == 'Dogpatch'):
		# 	return (999,998,'http://www.foundsf.org/images/c/ca/Pothill%24pelton-dwellings-in-dogpatch.jpg','Text',hood)
		# elif (hood == 'Downtown'):
		# 	return (999,998,'http://www.foundsf.org/images/4/4f/Hashbury%24downtown-view-1955.jpg','Text',hood)
		# elif (hood == 'Eureka Valley'):
		# 	return (999,998,'http://www.foundsf.org/images/0/00/Castro1%24eureka-valley-sw-c-1885.jpg','Text',hood)
		# elif (hood == 'Excelsior/Visitacion Valley'):
		# 	return (999,998,'http://www.foundsf.org/images/e/eb/Excelvis%24excelsior-picnic-1890.jpg','Text',hood)
		# elif (hood == 'Fisherman''s Wharf'):
		# 	return (999,998,'http://www.foundsf.org/images/d/de/Italian1%24fishermen_s-wharf-c-1900.jpg','Text',hood)
		# elif (hood == 'Glen Canyon'):
		# 	return (999,998,'http://www.foundsf.org/images/b/b4/Glenpark%24glen-canyon-rocks.jpg','Text',hood)
		# elif (hood == 'Glen Park'):
		# 	return (999,998,'http://www.foundsf.org/images/5/52/Glenpark%24castro-st-and-30th-1997.jpg','Text',hood)
		# elif (hood == 'Golden Gate Park'):
		# 	return (999,998,'http://www.foundsf.org/images/a/a8/Ggpk%24deer-1899.jpg','Text',hood)
		# elif (hood == 'Haight-Ashbury'):
		# 	return (999,998,'http://www.foundsf.org/images/4/43/Hashbury%24haight-and-clayton-1936.jpg','Text',hood)
		# elif (hood == 'Hayes Valley'):
		# 	return (999,998,'http://www.foundsf.org/images/9/9b/Westaddi%24ladies-protect-soc-1865.jpg','Text',hood)
		# elif (hood == 'Jordan Park'):
		# 	return (999,998,'http://www.foundsf.org/images/7/75/Westaddi%24laurel-hill-cemetery-1890s.jpg','Text',hood)
		# elif (hood == 'Lower Haight'):
		# 	return (999,998,'http://www.foundsf.org/images/f/f4/Buena_Vista_East_view_1886_AAB-8803.jpg','Text',hood)
		# elif (hood == 'Marina'):
		# 	return (999,998,'http://www.foundsf.org/images/7/7e/Marina%24pacific-heights-1895.jpg','Text',hood)
		# elif (hood == 'Mission'):
		# 	return (999,998,'http://www.foundsf.org/images/4/47/1905_16th-and-Folsom-streetcars-in-flood-SFPL-AAB-5929.jpg','Text',hood)
		# elif (hood == 'Mission Bay'):
		# 	return (999,998,'http://www.foundsf.org/images/9/9d/Pothill%24mission-bay-1885.jpg','Text',hood)
		# elif (hood == 'Nob Hill'):
		# 	return (999,998,'http://www.foundsf.org/images/0/0e/Rulclas1%24crockers-spite-fence%24mansion_itm%24crocker-mansion.jpg','Text',hood)
		# elif (hood == 'Noe Valley'):
		# 	return (999,998,'http://www.foundsf.org/images/5/5f/Noevaly1%2425th-st-and-dolores-1947.jpg','Text',hood)
		# elif (hood == 'North Beach'):
		# 	return (999,998,'http://www.foundsf.org/images/e/ea/Norbeach%24north-beach-1856.jpg','Text',hood)
		# elif (hood == 'OMI/Ingleside'):
		# 	return (999,998,'http://www.foundsf.org/images/b/b1/Urbano-sundial-1922.jpg','Text',hood)
		# elif (hood == 'Pacific Heights'):
		# 	return (999,998,'http://www.foundsf.org/images/8/89/Atherton_House_.jpg','Text',hood)
		# elif (hood == 'Polk Gulch'):
		# 	return (999,998,'http://www.foundsf.org/images/3/33/Tendrnob%24polk-gulch-1860s-view.jpg','Text',hood)
		# elif (hood == 'Portola'):
		# 	return (999,998,'http://www.foundsf.org/images/2/2d/Excelvis%24silver-avenue-west-c-1924.jpg','Text',hood)
		# elif (hood == 'Potrero Hill'):
		# 	return (999,998,'http://www.foundsf.org/images/2/21/Irish-hill-stump-cu.jpg','Text',hood)
		# elif (hood == 'Presidio'):
		# 	return (999,998,'http://www.foundsf.org/images/c/cf/Troops-mock-battle-1876.jpg','Text',hood)
		# elif (hood == 'Richmond'):
		# 	return (999,998,'http://www.foundsf.org/images/1/18/Richmond%24cablecar-clement-st-1940s.jpg','Text',hood)
		# elif (hood == 'Russian Hill'):
		# 	return (999,998,'http://www.foundsf.org/images/9/92/Norbeach%24lombard-street-1922-photo.jpg','Text',hood)
		# elif (hood == 'SOMA'):
		# 	return (999,998,'http://www.foundsf.org/images/6/61/Soma1%24soma-view-of-palace-hotel-1892.jpg','Text',hood)
		# elif (hood == 'Shoreline'):
		# 	return (999,998,'http://www.foundsf.org/images/c/c1/Marina%24crissy-field-marshes-1895.jpg','Text',hood)
		# elif (hood == 'Sunset'):
		# 	return (999,998,'http://www.foundsf.org/images/f/f8/Sunset_dunes_1947.jpg','Text',hood)
		# elif (hood == 'Telegraph Hill'):
		# 	return (999,998,'http://www.foundsf.org/images/9/9d/Coit-Tower_TELHILL_1930s.jpg','Text',hood)
		# elif (hood == 'TenderNob'):
		# 	return (999,998,'http://www.foundsf.org/images/1/10/Tendrnob%24nob-hill-1895.jpg','Text',hood)
		# elif (hood == 'Tenderloin'):
		# 	return (999,998,'http://www.foundsf.org/images/a/a4/Aunt_charlies_sign.jpg','Text',hood)
		# elif (hood == 'Twin Peaks'):
		# 	return (999,998,'http://www.foundsf.org/images/8/81/Sunset%24twin-peaks-photo.jpg','Text',hood)
		# elif (hood == 'West of Twin Peaks'):
		# 	return (999,998,'http://www.foundsf.org/images/7/70/Hawk-hill-and-st-francis-fountain_4430.jpg','Text',hood)
		# elif (hood == 'Western Addition'):
		# 	return (999,998,'http://www.foundsf.org/images/4/4b/Westaddi%24post-and-laguna-1927.jpg','Text',hood)
		# elif (hood == 'Westwood Park'):
		# 	return (999,998,'http://www.foundsf.org/images/f/f2/Westwood-highlands1963.jpg','Text',hood)
		# else:
		# 	return (999,998,'http://www.foundsf.org/images/1/11/Soma1%243rd-and-bryant-lofts.jpg','Text',hood)	
		
	def tagimage(self, imageid, pageid, latcoord, longcoord, hood, username):
		image = ImageModel(usernameupdated=username, imageid=int(imageid), pageid=int(pageid), latcoord=latcoord, longcoord=longcoord, neighborhood=hood)
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
			
chatapp = webapp.WSGIApplication([('/api/image', ImageEndpoint)])

def main(): 
	run_wsgi_app(chatapp)

if __name__ == "__main__": main()