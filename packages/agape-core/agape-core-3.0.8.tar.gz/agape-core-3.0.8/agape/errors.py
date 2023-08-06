
from rest_framework.response import Response


class ErrorResponse( Exception ):
	""" This is an exception which is caught by a Proxy sitting between a view and a model. The Proxy/View which catches this exception is to return the child HTTP Response. """

	def __init__( self, status_code, message ):

		self.response = Response( 
				{
					'message': message
				},
				status = status_code 
			)

		super().__init__( "Error {}: {}".format(status_code, message) )
