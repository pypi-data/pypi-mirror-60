
from agape.serializers import DynamicSerializer
import re

# holds all entity classes keyed by their entity token
registry = {}

def e(token):
	""" Return the entity class associated with the token. """
	return registry[token]


def tokenize( name ):
	""" Camel case to snake case. Used to create tokens from class names. """
	token = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
	token = re.sub('([a-z0-9])([A-Z])', r'\1-\2', token).lower()
	token = re.sub('_', '-', token)
	return token


class Query():
	""" 
	Layer over the model/queryset functionality. Let's build something cleaner. 
	Expiremental/Work in progress. This will accept 'filter' objects from the
	front end to perform queries on the database.
	"""

	def __init__(self, entity, *args, **kwargs):

		self.entity = entity

		self.queryset = entity.model.objects.filter( *args, **kwargs )


	def translate( self, schematic, *args, **kwargs ):
		""" Serialize the queryset. """
		# TODO: Is the best function name? When converting between types of data, I often refer to it as translation, because we are translating our description of an object. I think of objects as actaully existing in "abstract reality", when we go between formats such as a python object or a json string, we translating from one "language" or "format" to another. We are describe the same literal abstract object and describing it in different terms or formats.

		# default many=True when creating the serializer. as it stands queryset is
		# always going to be a list because we call .filter on it, not .get
		kwargs['many'] = kwargs.get('many', True)

		serializer = self.entity.get_serializer( schematic, self.queryset, *args, **kwargs )

		return serializer.data



class Entity():
	""" Base class for all entities. Abstract. """
	pass


class ModelEntity( Entity ):
	""" Base class for model entities. Abstract. This class is not intended to be instantiated. All Entity classes which have a model DERIVE from this class. """


	# Idea for lay over queryset/filter. Used in entity proxy for retrieving field
	# options in the meta data.
	@classmethod
	def query( cls, *args, **kwargs ):
		return Query( cls , *args, **kwargs )


	@classmethod
	def get_serializer( cls, schematic, *args, **kwargs ):

		serializer_class = cls.create_dynamic_serializer_class( cls.model, schematic )

		serializer = serializer_class( *args, **kwargs )

		return serializer

	# TODO: memoize this method? We should get the same serializer *class* if we call this method with the same schematic. This is probably low priority because it is not likely that we are calling this method with exact the same model and schematic in a single request. Will this have performace gains with a channels? If a socket is instaniated only 1 per connection and remains open over the lifetime of the connection, memoizing could have a significant performance impact.
	
	# NOTE: This method accepts the model as the 2nd argument. This seems counter intuititive because the model for this entity is already set on the class and accessible via the `model` property, however if we are serializing child objects, we need a way to create a dynamic serializer for the child object, even if it is not an @entity. Maybe this should be broken out into another function which is not a method, and this method calls that function with all the necessary arguments. For now, we always call this method and specify the model explicitly
	@classmethod
	def create_dynamic_serializer_class( cls, model, schematic ):

		from  django.db.models.fields import related_descriptors

		# print ( "create_dynamic_serializer_class")
		
		dynamic_model = model

		class _Serializer_( DynamicSerializer ):

			class Meta:

				model = dynamic_model

				fields = ['id']

				read_only_fields = ['id']


		for field in schematic:

			# dictionary field
			if isinstance( field, dict ):

				for fieldname, definition in field.items():

					# get the field descriptor from the model
					descriptor = getattr(_Serializer_.Meta.model, fieldname )

					if descriptor is None:

						raise Exception('Could not find field %s on model' % fieldname )


					# if Reverse ManyToOneField
					# django.db.models.fields.related_descriptors.ReverseManyToOneDescriptor
					if isinstance( descriptor, related_descriptors.ReverseManyToOneDescriptor ):

						related_model = descriptor.field.model

						related_serializer = cls.create_dynamic_serializer_class(
													related_model,
													definition
												)

						_Serializer_._declared_fields[fieldname] = related_serializer( many=True )

						_Serializer_.add_fields( fieldname )

					# if Forward ManyToOne Field
					# # django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor
					elif isinstance( descriptor, related_descriptors.ForwardManyToOneDescriptor ):
						related_model = descriptor.field.related_model

						related_serializer = cls.create_dynamic_serializer_class( 
													related_model, 
													definition 
												)
					

						_Serializer_._declared_fields[fieldname] = related_serializer()

						_Serializer_.add_fields( fieldname )

					else:

						raise Exception(
							'No implementation for %s ' % descriptor.__class__.__name__
						)


			else:

					_Serializer_.add_fields( field )



		return _Serializer_






class _meta_():
	""" If the model which is being acted upon by the @entity decorator does not have a meta class, a new meta class will be created for it using this class as a base. Therefore this class also outlines the default values which should be assigned to the meta class, should the meta-class exist but not define all these values explicitly."""

	icon = "all_out"

	fields = {}  # TODO: <--- is this used anywhere? I think it needs to be removed,
				 # it was replaced with the views property below

	views = {
		'list'  : [ 'primary_text', 'secondary_text' ],

		'edit'  : '*',

		'new'   : '*',

		'select': [ 'primary_text' ]
	}




def entity( cls ):
	""" This is the @entity decorator. The current implementation is only intended to be used on django Model classes, however other class types may be supported in the future. We do also use it on the 'App' class below, which will be used to query meta
	information about the app as a whole. """

	model = cls
	classname = model.__name__

	def configure_metaclass():
		""" If the target class does not have a meta class one is created for it using the _meta_ class as a base class. Default values for fields such as label, plural, tokens, and views are created dynamically if not set in the meta class. """

		if not hasattr( model, 'meta' ):

			class __meta__( _meta_ ):

				pass

			model.meta = __meta__

		meta = model.meta


		# label
		if not hasattr( meta, 'icon' ):
			meta.icon = 'all_out'

		# label
		if not hasattr( meta, 'label' ):
			meta.label = classname

		# plural
		if not hasattr( meta, 'plural' ):
			meta.plural = "%ss" % meta.label

		# token
		if not hasattr( meta, 'token' ):
			meta.token     = tokenize( meta.label )

		# plural
		if not hasattr( meta, 'tokens' ):
			meta.tokens     = "%ss" % meta.token

		# views list
		if not hasattr( meta, 'views' ):
			meta.views = { **_meta_.views }

		# merge default with existing
		else:
			meta.views = { **_meta_.views, **meta.views }

	configure_metaclass()


	class _Entity_( ModelEntity ):
		""" Dynamically created class specifically for this entity."""
		pass

	meta = model.meta
	_Entity_.model = model
	_Entity_.token = meta.token

	# set values on the decorated class
	model.entity = meta.token
	model.entity_plural = "%ss" % meta.token 

	# register the entity
	registry[ model.entity ] = _Entity_ 

	return cls


@entity
class App( Entity ):

	def query( cls, *args, **kwargs ):

		pass

	class meta:

		token = "app"
		tokens = "app"

		label = "App"
		plural = "App"



#
# 	Idea for a layer over the model queryset/filter. It should accept a filter dict or 
# 	which gets passed through Django filters, and ultimately returns an iterator over a 
# 	list of object, or the serialized version 
# 
#   class Query():

# 	def __init__(self, entity, *args, **kwargs):

# 		self.entity = entity

# 		self.queryset = entity.model.objects.filter( *args, **kwargs )


# 	def translate( self, schematic, *args, **kwargs ):


# 		serializer = self.entity.get_serializer( schematic, self.queryset, *args, **kwargs )

# 		return serializer.data