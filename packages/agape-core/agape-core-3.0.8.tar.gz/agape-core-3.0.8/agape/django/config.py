
from django.apps import AppConfig

from agape.signals import Scope, trigger

class DjangoAppConfig( AppConfig ):
	""" Triggers the app.ready event """

	def ready(self):

		scope = Scope()
		scope.config = self

		trigger("django.app.ready", scope )

		event = "django.app.{}.ready".format( self.name )
		print( event )
		trigger(event, scope )

		super().ready()



