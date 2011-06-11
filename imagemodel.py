from google.appengine.ext import db

class ImageModel(db.Model):
	imageurl = db.StringProperty()
	pageid = db.IntegerProperty() 
	neighborhood = db.StringProperty()
	latcoord = db.StringProperty()
	longcoord = db.StringProperty()
	usernameupdated = db.StringProperty()
	updatetime = db.DateTimeProperty(auto_now_add=True) 

def __str__(self): 
	return "%s, id (%s, %s) coords: %s at %s" % (self.imageurl, self.pageid, self.latcoord, self.longcoord, self.neighborhood, self.usernameupdated, self.updatetime)

