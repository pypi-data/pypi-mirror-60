from django.db import models



# ** DEPRECATED: DO NOT USE THIS **
class Model(models.Model):

	entity = 'undefined'

	def moniker(self):
		return '{}:{}'.format(self.entity, self.id)

	def __str__(self):
		return '<{}>'.format(self.moniker())

	class Meta:
		abstract = True


class DynamicModel():
	"""
	This is a mixin class. Add it to your models to expose the add_field
	method which can be used to Dynamically add properties to a model.
	"""

	@property
	def moniker(self):
		return '{}:{}'.format( self.entity, self.id )

	def __unicode__(self):
		return "<{}>".format( self.moniker )

	def __str__(self):
		return "<{}>".format( self.moniker )



	@classmethod
	def add_field(cls, *args, **kwargs ):

		# single argument is expect an instantiated field model
		if len(args) is 1:
			field = args[0]

			if field.name is None:
				raise ValueError("When passing in an already instantiated db field, it must have the attribute already set.")
			else:
				cls.add_to_class( field.name, field )

		else:
			name = args[0]
			constructor = args[1]

			try:
				args = args[2:]
			except Exception as err:
				args = list()

			# ensure db_column field is set correctly for ForeignKey fields
			from django.db.models import ForeignKey
			if constructor is ForeignKey and 'db_column' not in kwargs:
				kwargs['db_column'] = 'name' + '_id'


			field = constructor( *args, **kwargs, name=name )
			cls.add_to_class( name, field )






""" BooleanIntegerField

Use for database columns that are stored as integers but actually just use 1/0 to
represent True/False boolean values. This Field will provide True/False values for
use in python and store the data as 1s and 0s in the database.
"""
class BooleanIntegerField(models.NullBooleanField):

	def from_db_value(self, value, expression, connection, context):
		if value is None:
			return value

		return True if value else False

	def get_db_prep_value(self, value, connection, **kwargs):

		if value is None:
		  return value

		if value == True:
		  return 1
		else:
		  return 0

"""CSV Field
Transforms comma seperated values to a python list and vice versa.

"""
class CsvField(models.CharField):

	def from_db_value(self, value, expression, connection, context):
		if value is None:
		  return []
		else:
		  return list( map( lambda x:  x.strip(), value.split(',') ) )

	def get_db_prep_value(self, value, connection, **kwargs):

		if value is None:
		  return ''
		else:
		  return ','.join(value)

