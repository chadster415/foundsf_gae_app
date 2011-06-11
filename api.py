from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app 
import datetime

class WelcomePage(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/html" 
		self.response.out.write(
			"""<html> <head>
			<title>Welcome to MarkCC's chat service</title> </head>
			<body> <h1>Welcome to MarkCC's chat service</h1> <p> The current time is: %s</p>
			</body> </html>
			""" % (datetime.datetime.now()))
			
chatapp = webapp.WSGIApplication([('/', WelcomePage)])

def main(): 
	run_wsgi_app(chatapp)

if __name__ == "__main__": main()