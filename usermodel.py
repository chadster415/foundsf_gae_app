from google.appengine.ext import db

class UserModel(db.Model): 
	username = db.StringProperty(required=True)
	neighborhood = db.StringProperty()
	count = db.IntegerProperty(default=0) 
	updatetime = db.DateTimeProperty(auto_now_add=True) 

def __str__(self): 
	return "%s (%s): %s at %s" % (self.username, self.neighborhood, self.count, self.updatetime)