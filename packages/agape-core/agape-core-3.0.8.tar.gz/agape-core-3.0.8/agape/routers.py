from django.conf.urls import url
from rest_framework.routers import Route, DynamicRoute, SimpleRouter

from agape.viewsets import CrudViewSet

class CrudRouter( SimpleRouter ):

	def register( self, model, serializer_class, prefix=None, basename=None, viewset=CrudViewSet, **kwargs ):

		if basename is None:
			basename = model.entity

		if prefix is None:
			prefix = model.entity_plural

		self.registry.append( 
			( prefix, viewset, basename, model, serializer_class, kwargs ) 
		)

		# invalidate the urls cache
		if hasattr(self, '_urls'):
			del self._urls



	def get_urls( self ):
		"""
		Use the registered viewsets to generate a list of URL patterns.
		"""
		ret = []

		for prefix, viewset, basename, model, serializer_class, kwargs in self.registry:
			# lookup = '(?P<pk>[^/.]+)'
			lookup = self.get_lookup_regex(viewset)
			routes = self.get_routes( viewset )

			for route in routes:

				# Only actions which actually exist on the viewset will be bound
				mapping = self.get_method_map( CrudViewSet, route.mapping)
				if not mapping:
					continue

				# Build the url pattern
				regex = route.url.format(
					prefix=prefix,
					lookup=lookup,
					trailing_slash=self.trailing_slash
				)

				# If there is no prefix, the first part of the url is probably
				#   controlled by project's urls.py and the router is in an app,
				#   so a slash in the beginning will (A) cause Django to give
				#   warnings and (B) generate URLS that will require using '//'.
				if not prefix and regex[:2] == '^/':
					regex = '^' + regex[2:]

				initkwargs = route.initkwargs.copy()
				initkwargs.update({
					'basename': basename,
					'detail': route.detail,
				})

				view = viewset.as_view(mapping, 
					context=model.entity, 
					model=model, 
					serializer_class=serializer_class, 
					**initkwargs
				)

				name = route.name.format(basename=basename)
				
				ret.append(url(regex, view, name=name))

		return ret


		# ret = []

		# for prefix, 


		# for prefix, viewset, basename in self.registry:
		#     lookup = self.get_lookup_regex(viewset)
		#     routes = self.get_routes(viewset)

		#     for route in routes:

		#         # Only actions which actually exist on the viewset will be bound
		#         mapping = self.get_method_map(viewset, route.mapping)
		#         if not mapping:
		#             continue

		#         # Build the url pattern
		#         regex = route.url.format(
		#             prefix=prefix,
		#             lookup=lookup,
		#             trailing_slash=self.trailing_slash
		#         )

		#         # If there is no prefix, the first part of the url is probably
		#         #   controlled by project's urls.py and the router is in an app,
		#         #   so a slash in the beginning will (A) cause Django to give
		#         #   warnings and (B) generate URLS that will require using '//'.
		#         if not prefix and regex[:2] == '^/':
		#             regex = '^' + regex[2:]

		#         initkwargs = route.initkwargs.copy()
		#         initkwargs.update({
		#             'basename': basename,
		#             'detail': route.detail,
		#         })

		#         view = viewset.as_view(mapping, **initkwargs)
		#         name = route.name.format(basename=basename)
		#         ret.append(url(regex, view, name=name))

		# return ret
