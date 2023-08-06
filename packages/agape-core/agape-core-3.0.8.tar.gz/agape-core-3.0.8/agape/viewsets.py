from agape.signals import trigger
from rest_framework import permissions,status,views,viewsets
from rest_framework.response import Response

from agape.proxies import ModelProxy




class CrudViewSet( viewsets.ModelViewSet ):

	context = None
	model   = None
	serializer_class = None


	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		self.proxy = ModelProxy( self.context, self.model, self.serializer_class )


	def create( self, request, *args, **kwargs ):

		self.proxy.create( **kwargs, request=request )

		return self.proxy.response

	def retrieve( self, request, *args, **kwargs ):

		self.proxy.retrieve( **kwargs, request=request )

		return self.proxy.response

	def update( self, request, *args, **kwargs ):

		self.proxy.update( **kwargs, request=request )

		return self.proxy.response

	def destroy( self, request, *args, **kwargs ):

		self.proxy.destroy( **kwargs, request=request )

		return self.proxy.response

	def list( self, request, *args, **kwargs ):

		self.proxy.list( **kwargs, request=request )

		return self.proxy.response



	# def initial( self, request, *args, **kwargs ):

	# 	self.scope = Scope( **kwargs, request=request )

	# 	super().initial( request, *args, **kwargs )

	# 	pass


# DEPRECATED: Use CRUD View Set
class ModelViewSet(viewsets.ModelViewSet):


	scope = {}


	def new_scope( self, request, *args, **kwargs ):
		""" 
		Creates a scope from view parameters .

		Scopes exist for the lifetime of the view and are available to any
		events that are triggered during the view lifecycle.
		"""
		return  {
			'request': request,
			'args': [ *args ],
			'kwargs': { **kwargs },
			'data': request.data.copy(),
			'view': self
		}



	def initial( self, request, *args, **kwargs ):
		""" Called before any method handle. """
		self.scope = self.new_scope(  request, *args, **kwargs )
		super().initial( request, *args, **kwargs )
		pass

	def create(self, request, *args, **kwargs):

		scope = self.scope

		# emit signal
		trigger(self.context+'.create:request', scope, request )

		# get a copy of the request data
		data = scope.get('data', None)
		trigger(self.context+'.create:before', scope, data )

		# create new instance
		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		instance = self.perform_create(serializer)
		scope['instance'] = instance
		trigger(self.context+'.create:success', scope, instance)

		# serialize instance data
		serializer = self.get_serializer(instance)
		serialized_data = serializer.data
		scope['serialized_data'] = serialized_data
		trigger(self.context+'.create:serialize', scope, serialized_data)		

		# return a response
		headers = self.get_success_headers(serialized_data)
		response = Response(serialized_data, status=status.HTTP_201_CREATED, headers=headers)
		scope['response'] = response
		trigger(self.context+'.create:response', scope, response)

		self.scope = None
		return response


	def perform_create(self, serializer):
		instance = serializer.save()
		return instance

	def retrieve(self, request, *args, **kwargs):

		scope = self.scope

		trigger(self.context+'.retrieve:before',scope)

		scope.instance = self.get_object( scope.pk )
		trigger(self.context+'.retrieve:success',scope, instance)

		serializer = self.get_serializer(instance)
		data = serializer.data
		trigger(self.context+'.retrieve:serialize',scope,data)

		response = Response(data)
		trigger(self.context+'.retrieve:response',scope,response)
		return response

	def update(self, request, *args, **kwargs):

		# scope
		scope = { 'request': request }

		trigger(self.context+'.update:request',scope,request,*args,**kwargs)

		partial = kwargs.pop('partial', False)        
		instance = self.get_object()
		trigger(self.context+'.update:retrieve',scope,instance)

		data = kwargs.get('data') or request.data
		trigger(self.context+'.update:before',scope,data)

		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		instance = self.perform_update(serializer)
		trigger(self.context+'.update:success',scope,instance)
        
		data = serializer.data
		trigger(self.context+'.update:serialize',scope,data)	

		response = Response(data)
		trigger(self.context+'.update:response',scope,response)
		return response

	def perform_update(self, serializer):
		instance = serializer.save()
		return instance

	def destroy(self, request, *args, **kwargs):

		# scope
		scope = { 'request': request }

		trigger(self.context+'.destroy:request',scope,request,*args,**kwargs)
		
		instance = self.get_object()
		trigger(self.context+'.destroy:before',scope,instance)

		self.perform_destroy(instance)
		trigger(self.context+'.destroy:success',scope,instance)

		response = Response(status=status.HTTP_204_NO_CONTENT)
		trigger(self.context+'.destroy:response',scope,response)

		return response

	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
		    serializer = self.get_serializer(page, many=True)
		    return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)      

	def perform_destroy(self, instance):
		instance.delete()


