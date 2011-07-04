from google.appengine.ext import webapp, db 
from google.appengine.ext.webapp.util import run_wsgi_app 
import os, logging, util, showquery
from usermodel import UserModel
from imagemodel import ImageModel

class UserEndpoint(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/xml"
		op = util.getqsvalue('op')
		hood = util.getqsvalue('hood')
		oldusernames = util.getqsvalue('past')
		username = self.getusername()
		success = None
		if (op == 'add' and username is not None):
			try:
				success = self.adduser(username)
				a=('response',[('username',username),('score',0),('success',success)])
				self.response.out.write(util.toxml(a))
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))
						
		elif (op == 'update' and hood is not None):
			try:
				success = self.updateuser(username,hood)
				a=('response',[('username',username),('success',success)])
				self.response.out.write(util.toxml(a))
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))
				
		elif (username is not None):
			try:
				user = util.getuser(username)
				success, score = self.getusercount(username, oldusernames)
				a=('response',[('username',username),('neighborhood',user.neighborhood),('score',score),('updated',user.updatetime),('success',success)])
				self.response.out.write(util.toxml(a))
			except Exception, err:
				logging.error(err)
				self.response.out.write(util.toxml(('response',[('success',False)])))	
				
		#else:
			#self.response.out.write(util.toxml(('response',[('success',False)])))

	def adduser(self, username):
		user = util.getuser(username)
		if (user is not None):
			return False
			
		user = UserModel(username=username, count=0)
		try:
			user.put()
			return True
		except Exception, err:
			logging.error(str(err))
			
	def updateuser(self, username, hood):
		user = util.getuser(username)
		if (user is not None):
			try:
				user.neighborhood = hood
				user.put()
				return True
			except Exception, err:
				logging.error(str(err))
		else:
			return False		

	def getusername(self):
		path = os.environ["PATH_INFO"]
		tokens = path.split("/")
		username = tokens[3]
		return username
		
		
	def getusercount(self, username, oldusernames):
		if (oldusernames != None and len(oldusernames) > 0):
			usernamearray = oldusernames.split(",")
			usernamearray.append(username)
		else:
			usernamearray = [username]
		
		logging.info("Username is:" + ' '.join(usernamearray))		
		users = db.GqlQuery("SELECT * FROM UserModel WHERE username in :1", usernamearray)
		count = 0
		for user in users:
			count += user.count
		logging.info("Count is:" + str(count))
		return True, count						

			
app = webapp.WSGIApplication([('/api/user/.*', UserEndpoint)])

def main(): 
	run_wsgi_app(app)

if __name__ == "__main__": main()