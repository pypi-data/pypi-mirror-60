
""" Registry of observers keyed by event """
observers = {}



class Observer():
	"""
	Observe events and react to them by executing a callback.
	"""

	event     = None
	callback  = None
	data      = None

	def __init__(self, event, callback, data=None):
		self.event    = event
		self.callback = callback
		self.data     = data


	def destroy(self):
		""" 
		Remove this observer from the list of observers attached to the event.
		"""
		observers[self.event].remove(self)


	def react(self, scope, *args, **kwargs):
		"""
		React to an event by executing the callback.
		"""
		self.callback( self, scope, *args, *kwargs)


class Scope():

	def __init__( self, **kwargs ):
		self.__dict__.update(kwargs)

		if 'request' in kwargs and not 'data' in kwargs:
			self.data = self.request.data.copy()

	def get( self, attr, default=None ):

		if hasattr( self, attr ):
			return getattr( self, attr )
		else:
			return default



def on( event, callback, data=None ):
	""" Observe an event and react to it with a callback. """
	
	# create the observer
	observer = Observer( event, callback, data )

	# store the observer under that event
	observers[event] = observers.get(event,[])
	observers[event].append( observer )

	return observer

# TODO: Possibly import "wraps"
# from functools import wraps
# https://dev.to/apcelent/python-decorator-tutorial-with-example-529f#targetText=Python%20decorator%20are%20the%20function,match%20the%20function%20to%20decorate.
def connect( event, data=None ):

	def inner( callback ):
		on( event, callback, data )
		return callback

	return inner


def trigger(event, scope, *args, **kwargs):
	""" Trigger all callbacks for an event. """

	for observer in observers.get(event,[]):
		observer.react( scope, *args, **kwargs )

