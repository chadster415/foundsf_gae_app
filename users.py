from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app 
import util, logging
from usermodel import UserModel

class UsersEndpoint(webapp.RequestHandler): 
	
	def get(self):
		self.response.headers["Content-Type"] = "text/xml"
		op = util.getqsvalue('op','scores')
		count = util.getqsvalue('count', 10)
				
		if (op == 'scores'):
			self.writescores(count)
		
	def writescores(self, count):
		#do a gql query to get the top [count] users by scores desc
		q = UserModel.all()
		q.order('-count')
		results = q.fetch(int(count))
		logging.info(results)
		rank = 1
		a = []
		for user in results:
			b = ('user',[('username',user.username),('score',user.count),('neighborhood',user.neighborhood)],{'rank':rank})
			a.append(b)
			rank = rank + 1

		c=('response',
			[('users',a,{'page':count,'found':rank - 1})])
				
		# c=('response',
		# 			[('users',[
		# 				('user',[('username','chada'),('count',112),(neighborhood,'Castro')],{'rank':1}),
		# 				('user',[('username','chada'),('count',142),(neighborhood,'Mission')],{'rank':2}),
		# 				('user',[('username','chada'),('count',152),(neighborhood,'SOMA')],{'rank':3}),
		# 				],
		# 			{'page':count,'found':found})])
					
		self.response.out.write(util.toxml(c))
							
app = webapp.WSGIApplication([('/api/users', UsersEndpoint)])

def main(): 
	run_wsgi_app(app)

if __name__ == "__main__": main()