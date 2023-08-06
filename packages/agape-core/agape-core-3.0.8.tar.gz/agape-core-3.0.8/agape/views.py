from rest_framework.views import APIView

from .proxies import DataProxy, EntityProxy
from .entity import e

class UnifiedView( APIView ):


	def create_proxy( self ):

		# self.proxy = DataProxy( self.entity, self.schematic )
		self.proxy = EntityProxy( e(self.entity) )

		return self.proxy


	def determine_pk( self ):

		## if the request has a 'pk'
		if 'pk' in self.request.data:
			self.kwargs['pk'] = self.request.data.get('pk', None)

		## if the data has an 'id'
		elif 'data' in self.kwargs:
			self.kwargs['pk'] = self.kwargs['data'].pop('id', None)


	def parse_route( self, action ):

		route = action.split('.')

		# if action has one argument - assume the entity has been
		# set using the entity property
		if len(route) == 1:

			self.action = route[0]


		# if action has two arguments, we have a entity.action
		# route, break it out into is component properties
		else:

			self.entity = route[0]

			self.action = route[1]


	def parse_request( self, request, *args, **kwargs ):

		self.args = args

		self.kwargs = kwargs

		self.request = request

		self.packet = request.data.copy()

		for key, value in self.packet.items():

			self.kwargs[key] = value

		self.parse_route( request.data.get('action') )

		# TODO: I think? I want this cleaner? Maybe not. Allow specifying the 
		# entity/action on the packet indiviudally as is currenlty implemented, or force the use of routing with entity.action
		if not hasattr(self, 'entity') and kwargs.get('entity'):

			self.entity = kwargs['entity']

		self.determine_pk( )


	def perform_request( self ):

		method = getattr( self.proxy, self.action )

		method( request=self.request, **self.kwargs )


	def post( self, request, *args, **kwargs):

		self.parse_request( request, *args, **kwargs )

		self.create_proxy()

		self.perform_request()

		return self.proxy.response
