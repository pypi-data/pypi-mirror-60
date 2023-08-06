from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.generics import GenericAPIView

from agape import signals
from agape.errors import ErrorResponse
from agape.signals import Scope







class BaseProxy( ):

	def __init__( self, context ):

		if isinstance( context, list ):
			self.context = context
		else:
			self.context = [ context ]


	def new_scope(self, **kwargs):

		self.scope = Scope( **kwargs )

		return self.scope


	def get_success_headers(self, data):
		try:
			return {'Location': str(data[api_settings.URL_FIELD_NAME])}
		except (TypeError, KeyError):
			return {}


	def respond( self, status, data=None ):

		# TODO: Don't call get_success_headers here if the status code is not a success status code. As it stands (v2.6.0 Dec 24, 2019) this function is only called with successful status codes, non-successful status codes are returned in the proxy when an ErrorReponse is thrown 
		response = Response( 
			data, 
			status=status, 
			headers=self.get_success_headers(data)
		)

		self.scope.response = response
		return response



	def trigger(self, action, stage, scope):

		for context in self.context:

			event = "{}.{}:{}".format( context, action, stage )

			signals.trigger( event, scope )	


	@property
	def request(self):
		return self.scope.request


	@property
	def instance(self):
		return self.scope.instance


	@property
	def items(self):
		return self.scope.items
	

	@property
	def serialized_data(self):
		return self.scope.serialized_data


	@property
	def response(self):
		return self.scope.response



class EntityProxy ( BaseProxy ):
	""" This proxy is used by the UnifiedView to handle CRUD operations on entities."""

	# TODO: Add events to this proxy such as those in the ModelProxy

	def __init__( self, entity ):

		self.entity = entity

		self.context = entity.token


	def get_meta( self ):
		""" Return meta data for fields existing in the schematic. """

		# used when kwargs[meta]=True OR when performing a meta-query

		# iterate over each field in the model
		schema = self.scope.schematic
		struct = {}

		# entity meta
		struct['entity'] = {
			'token': self.entity.token,
			'label': self.entity.model.meta.label,
		}

		# get foreign key options
		def get_foreign_key_options( field ):

			from agape.entity import e

			# query with no filter, get all options
			query = e(field.related_model.entity).query()

			schematic =  ['id','select_text']

			options = query.translate( schematic )

			return options

		# data meta
		datameta = []
		for field in self.entity.model._meta.local_fields:

			if field.name in schema:

				meta = {
					'field': field.name,
					'label': field.name.capitalize(), # TODO: Get label from meta values for the field, or default to field.name.captialize()
					'native' : field.__class__.__name__,
				}

				# get meta fields specified directly on the field class
				if hasattr(field, 'meta'):
					meta = { **meta, **field.meta }

				# get meta fields specified on the models meta class
				if hasattr( self.entity.model.meta, 'fields' ):
					if field.name in self.entity.model.meta.fields:
						meta = { **meta, **self.entity.model.meta.fields[field.name] }


				if meta['native'] is "ForeignKey":

					options = get_foreign_key_options( field )

					meta['options'] = options


				datameta.append(meta)

		struct['data'] = datameta
		return struct



	def get_object( self, pk ):

		if pk == 0:
			return self.entity.model()

		else:

		# try:
			return self.entity.model.objects.get(pk=pk)
		# except:
		# 	raise ErrorResponse('404', "Does not exist" )


	def get_queryset( self ):

		return self.entity.model.objects.all()


	def get_schematic( self ):
		""" Get the schematic for the response."""

		# if respond attr has not been set on the the scope, try the
		# schematic attribue, if that has not been set, return an empty 
		# list
		if hasattr( self.scope, 'respond' ):
			schematic = self.scope.respond
		elif hasattr( self.scope, 'schematic' ):
			schematic = self.scope.schematic
		else:
			schematic =  []


		# if the schematic is a string instead of an array of fields
		# then get the schematic with the correseponding name from the
		# meta class of the entity
		if isinstance( schematic, str ):

			schemaname = schematic

			if schematic != '*':
				schematic  = self.entity.model.meta.views.get(schemaname)

			if isinstance( schematic, str ) and schematic == "*":

				schematic = self.get_model_fields( self.entity.model )


		self.scope.schematic = schematic

		return schematic

	def get_schematic_from_payload( self, data ):

		schematic = []

		for field, value in data.items():

			schematic.append( field )

		return schematic

	def get_model_fields( self, model ):
		# used by get_schematic - if the user specified schematic is a * for wildcard
		# we return all fields from the model to use as the schematic.
		# 
		# TODO: It is possible we will want to add the ability to set permissions on a
		# field-by-field basis, that means if certain fields have been restricted, we 
		# need to account for that in this function and rename it to something like 
		# get_schematic_from_permitted_fields_on_model

		schematic = [] 

		for field in model._meta.local_fields:

			schematic.append( field.name )

		return schematic


	def create( self, **kwargs ):

		action = "create"

		try:
			scope = self.new_scope( **kwargs )

			schematic = self.get_schematic_from_payload( scope.data )

			serializer = self.entity.get_serializer( schematic ,data=scope.data )

			serializer.is_valid(raise_exception=True)

			scope.is_valid=True

			scope.instance = serializer.save()

			scope.schematic = self.get_schematic()

			serializer = self.entity.get_serializer( scope.schematic, scope.instance )

			scope.data = serializer.data

			packet = self.create_packet()

			self.respond('201', packet )

			return True

		except ErrorResponse as e:

			# TODO: Catching Error Responses is untested

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False




	def list( self, **kwargs ):

		action = "list"

		try:
			scope = self.new_scope( **kwargs )

			schematic = self.get_schematic()

			scope.queryset = self.get_queryset()

			scope.items = list( scope.queryset )

			serializer  = self.entity.get_serializer( schematic, scope.items, many=True )

			scope.data = serializer.data

			packet = self.create_packet()

			scope.response = self.respond( '200', packet )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False

	def meta( self, **kwargs ):

		print( 'proxy.meta' )

		action = 'meta'

		print( kwargs )

		try:

			scope = self.new_scope( **kwargs )

			schematic = self.get_schematic()

			scope.data = None

			scope.meta = True

			packet = self.create_packet()

			scope.response = self.respond( '200', packet )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False

	def retrieve( self, **kwargs ):

		action = 'retrieve'

		try:
			scope = self.new_scope( **kwargs )

			schematic = self.get_schematic()

			scope.instance = self.get_object( scope.pk )

			serializer = self.entity.get_serializer( schematic, scope.instance )

			scope.data = serializer.data

			packet = self.create_packet()

			scope.response = self.respond( '200', packet )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False


	def update(self,  **kwargs):

		action = 'update'

		try:

			scope = self.new_scope( **kwargs )

			schematic = self.get_schematic_from_payload( scope.data )

			scope.instance = self.get_object( scope.pk )

			serializer = self.entity.get_serializer( 
				schematic       , scope.instance, 
				data=scope.data , partial=True 
				)

			serializer.is_valid(raise_exception=True)
			scope.is_valid=True

			scope.instance = serializer.save()

			scope.data = None

			packet = self.create_packet()

			scope.response = self.respond('200', packet )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False

	def destroy( self, **kwargs ):

		try:
			scope = self.new_scope( **kwargs )

			scope.instance = self.get_object( scope.pk )

			scope.instance.delete()

			scope.response = self.respond( '204' )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False


	def query( self,  **kwargs ):
		# TODO: This probably needs a better name. This returns information about the
		# entities in the registry. This can be used to "query" the application. 
		# That's where the name comes from. It's not querying the database, but
		# performing a 
		# meta-query on the actual app. When used in conjunction with the front-end 
		# components, a basic CRUD app can be created by specifying nothing more than 
		# just the model spec. meta-query probably isn't the right word as that already
		# refers to when we want to get meta information about the fields/properties/
		# attributes of an @entity - this query is a level higher - we are getting meta 
		# data about the entity itself, not of it's fields

		action = 'query'

		try:
			self.scope = Scope(**kwargs )

			self.scope.schematic = [ 'token', 'tokens', 'label', 'plural', 'icon' ]

			from agape.entity import registry

			entities = []

			for token, entity in registry.items():

				if token != "app":

					e = {
						'token': entity.model.meta.token,
						'tokens': entity.model.meta.tokens,
						'label': entity.model.meta.label,
						'plural': entity.model.meta.plural,
						'icon': entity.model.meta.icon,
					}

					entities.append( e )

			self.scope.data = entities

			packet = self.create_packet()

			self.scope.response = self.respond( '200', packet )

			return True

		except ErrorResponse as e:

			self.scope.response = e.response

			self.trigger( action, 'error', scope )

			return False


	def create_packet( self ):

		packet = {
			'entity': self.entity.token,
		}

		if self.scope.get('data'):
			packet['data'] = self.scope.data

		if 'data' in packet:
			packet['describe'] = self.scope.get('schematic', [] )

		if self.scope.get('meta'):
			packet['meta'] = self.get_meta()

		return packet











# TODO: Should ModelProxy really be a GenericAPIView? The only reason it this base class was used is because I wanted quick access to the paginate functionality provide through REST Framework. If that functionality is moved over the GenericAPIView base class can be removed. The primary argument/desire for wanting to remove that base class is that ModelProxy ISN'T an APIView. It's a proxy between the view and the model, NOT a view. Toe-mae-toe toe-mah-toe? Maybe, but it maybe a distinction worth putting a hard line between.

class ModelProxy( GenericAPIView ):
	""" Used by viewsets.CrudViewSet to create API views. """

	def __init__(self, context, model, serializer_class ):

		if isinstance( context, list ):
			self.context = context
		else:
			self.context = [ context ]

		self.model   = model
		self.serializer_class = serializer_class

	def get_object( self, pk ):

		try:
			return self.model.objects.get(pk=pk)
		except:
			raise ErrorResponse('404', "Does not exist" )

	def get_queryset( self ):

		return self.model.objects.all()

	def get_serializer(self, *args, **kwargs):
		return self.serializer_class( *args, **kwargs )


	def get_success_headers(self, data):
		try:
			return {'Location': str(data[api_settings.URL_FIELD_NAME])}
		except (TypeError, KeyError):
			return {}

	def new_scope(self, **kwargs):
		self.scope = Scope( **kwargs )
		return self.scope

	@property
	def request(self):
		return self.scope.request

	@property
	def instance(self):
		return self.scope.instance

	@property
	def items(self):
		return self.scope.items
	

	@property
	def serialized_data(self):
		return self.scope.serialized_data

	@property
	def response(self):
		return self.scope.response
	
	
	def trigger(self, action, stage, scope):

		for context in self.context:

			event = "{}.{}:{}".format( context, action, stage )

			# print ( event )

			signals.trigger( event, scope )


	def create(self, **kwargs):

		action="create"

		try:
			scope = self.new_scope( **kwargs )

			self.trigger( action, 'request', scope )

			self.trigger( action, 'before' , scope )

			# create new instance
			serializer = self.get_serializer(data=scope.data)
			serializer.is_valid(raise_exception=True)
			scope.instance = serializer.save()

			self.trigger( action, 'success', scope )

			# serialize instance data
			serializer = self.get_serializer(scope.instance)
			scope.serialized_data = serializer.data

			self.trigger( action, 'serialize', scope )

			scope.response = self.respond( '201', scope.serialized_data )

			self.trigger( action, 'response', scope )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False




	def retrieve(self,  **kwargs):

		action = 'retrieve'

		try:
			scope = self.new_scope( **kwargs )

			self.trigger( action, 'request', scope )

			self.trigger( action, 'before' , scope )

			scope.instance = self.get_object( scope.pk )
			self.trigger( action, 'success', scope )

			serializer = self.get_serializer( scope.instance )
			scope.serialized_data = serializer.data
			self.trigger( action, 'serialize', scope )

			scope.response = self.respond( '200', scope.serialized_data )
			self.trigger( action, 'response', scope )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False




	def update(self,  **kwargs):

		action = 'update'

		try:
			scope = self.new_scope( **kwargs )
			partial = kwargs.pop('partial', True)  
			self.trigger( action, 'request', scope )

     
			scope.instance = self.get_object( kwargs.get('pk') )
			self.trigger( action, 'before' , scope )

			serializer = self.get_serializer(
					scope.instance, 
					data=scope.data, 
					partial=partial
			)
			serializer.is_valid(raise_exception=True)
			scope.is_valid=True

			self.trigger( action, 'valid', scope )

			scope.instance = serializer.save()
			self.trigger( action, 'success', scope )

			scope.serialized_data = serializer.data
			self.trigger( action, 'serialize', scope )

			scope.response = self.respond( '200', serializer.data )
			self.trigger( action, 'response', scope )
	        
			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False


	def destroy(self, **kwargs):
		
		action="destroy"

		try:
			scope = self.new_scope( **kwargs )
			self.trigger( action, 'request', scope )

			scope.instance = self.get_object( scope.pk )
			self.trigger( action, 'before' , scope )

			scope.instance.delete()
			self.trigger( action, 'success', scope )

			scope.response = Response(status=status.HTTP_204_NO_CONTENT)
			self.trigger( action, 'response', scope )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False


	def list(self, **kwargs):

		action="list"

		try:
			scope = self.new_scope( **kwargs )
			self.trigger( action, 'request', scope )

			self.trigger( action, 'before' , scope )

			scope.queryset = self.filter_queryset( self.get_queryset() )
			scope.page = self.paginate_queryset( scope.queryset )

			if scope.page is not None:
				scope.items = list( scope.page )
				self.trigger( action, 'success', scope )

				serializer = self.get_serializer( scope.items, many=True)
				scope.serialized_data = serializer.data
				self.trigger( action, 'serialize', scope )

				scope.response = self.get_paginated_response(serializer.data)
				self.trigger( action, 'response', scope )

				return True

			else:
				scope.items = list( scope.queryset ) 
				self.trigger( action, 'success', scope )

				serializer  = self.get_serializer( scope.items, many=True)
				scope.serialized_data = serializer.data
				self.trigger( action, 'serialize', scope )

				scope.response = self.respond('200', scope.serialized_data )
				self.trigger( action, 'response', scope )

				return True


		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False



	def respond( self, status, data ):
		response = Response( 
			data, 
			status=status, 
			headers=self.get_success_headers(data)
		)

		self.scope.response = response
		return response





class DataProxy( ModelProxy ):
	""" Intermediary between ModelProxy and EntityProxy, a DataProxy works
	like a ModelProxy except you do not need to provide it with a serializer, instead it uses a schematic to create a serializer dynamically. This can be used in an APIView to provide a non-dynamic interface (REST) without the need to hard code the serializer."""

	# TODO: This should not use entities at all. As it stands create_dynamic_serializer exists on the entity class. It should exist as a free-standing function inside the agape.serializers package. Once that happens we can remove all references to entity inside this proxy. This class should not be entity aware.


	def __init__( self, entity, schematic=None ):

		self.entity = entity

		self.schematic = schematic

		super().__init__( entity.model.entity, entity.model, None )


	def get_serializer(self, *args, **kwargs):

		schematic = kwargs.pop('schematic')

		return self.entity.get_serializer( self.schematic, *args, **kwargs )


	def retrieve( self, *args, **kwargs ):

		kwargs['respond'] = kwargs.get('respond', ['id'] )

		try:
			scope = self.new_scope( **kwargs )

			schematic = scope.respond

			scope.instance = self.get_object( scope.pk )

			serializer = self.entity.get_serializer( schematic, scope.instance )

			scope.serialized_data = serializer.data

			scope.response = self.respond( '200', scope.serialized_data )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False




	def create(self, **kwargs):

		action="create"

		respond_schematic = kwargs.pop('respond', [] )  # <---------

		# print ( respond_schematic )

		try:
			scope = self.new_scope( **kwargs )

			self.trigger( action, 'request', scope )

			self.trigger( action, 'before' , scope )

			# create new instance
			serializer = self.get_serializer(data=scope.data)
			serializer.is_valid(raise_exception=True)
			scope.instance = serializer.save()

			self.trigger( action, 'success', scope )

			# serialize instance data
			serializer = self.get_serializer(scope.instance, fields=respond_schematic ) # <---------
			scope.serialized_data = serializer.data

			self.trigger( action, 'serialize', scope )

			scope.response = self.respond( '201', scope.serialized_data )

			self.trigger( action, 'response', scope )

			return True

		except ErrorResponse as e:

			scope.response = e.response

			self.trigger( action, 'error', scope )

			return False
