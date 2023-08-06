from django.db.models import CharField, SlugField, TextField, EmailField
from django.db.models import FileField, ImageField
from django.db.models import BooleanField, DecimalField, FloatField, IntegerField 
from django.db.models import DateField, TimeField, DateTimeField, DurationField
from django.db.models import ForeignKey

from django.db.models import CASCADE  as cascade , PROTECT as protect
from django.db.models import SET_NULL as set_null, SET_DEFAULT as set_default


def boolean( *args, **kwargs ):

	meta = _kwargs_( kwargs )

	meta['type'] = 'boolean'

	field = BooleanField( *args, **kwargs )

	field.meta = meta

	return field


def date( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'date'

	field = DateField( *args, **kwargs )

	field.meta = meta

	return field


def datetime( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'datetime'

	field = DateTimeField( *args, **kwargs )

	field.meta = meta

	return field


def decimal( max_digits, decimal_places, *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'decimal'

	kwargs['max_digits'] = max_digits

	kwargs['decimal_places'] = decimal_places

	field = DecimalField( *args, **kwargs )

	field.meta = meta

	return field

def duration( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'duration'

	field = DurationField( *args, **kwargs )

	field.meta = meta

	return field


def email( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'email'

	field = EmailField( *args, **kwargs )

	field.meta = meta

	return field


def file( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'float'

	field = FileField( *args, **kwargs )

	field.meta = meta

	return field


def float( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'file'

	field = FloatField( *args, **kwargs )

	field.meta = meta

	return field


def image( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'image'

	field = ImageField( *args, **kwargs )

	field.meta = meta

	return field


def integer( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'integer'

	field = IntegerField( *args, **kwargs )

	field.meta = meta

	return field


def join( model, policy, *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'entity'

	kwargs['on_delete'] = policy

	field = ForeignKey( model, *args, **kwargs )

	field.meta = meta

	return field

def slug( max_length, *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'slug'

	field = SlugField( *args, **kwargs )

	field.meta = meta

	return field


def string( max_length, *args, **kwargs ):

	meta = _kwargs_( kwargs )

	meta['type'] = 'string'

	field = CharField( max_length=max_length, *args, **kwargs )

	field.meta = meta

	return field

def time( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'time'

	field = TimeField( *args, **kwargs )

	field.meta = meta

	return field


def text( *args, **kwargs ):
	
	meta = _kwargs_( kwargs )

	meta['type'] = 'text'

	field = TextField( *args, **kwargs )

	field.meta = meta

	return field


# provide default aguments to the django db types based on the parameters
# to the factory function. add and remove kwargs as needed, kwargs is modified inline
# meaning it will affect the kwargs in the calling function. Returns a meta dict
# which is to be attached to the field as the meta property.
def _kwargs_( kwargs ):

	meta = {}
	meta['required'] = kwargs.pop( 'required', False )

	if meta['required']:
		kwargs['null']  = False
		kwargs['blank'] = False
	else:
		kwargs['null']  = True
		kwargs['blank'] = True

	return meta