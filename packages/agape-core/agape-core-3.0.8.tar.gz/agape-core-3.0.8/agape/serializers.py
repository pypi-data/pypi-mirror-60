from rest_framework import serializers
import copy 


class DynamicSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    coerce = True

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


    def coerce_foreign_key_values(self, data):

        """ Converts dictionary representation of objects or foreign key values to
        object instances when deserializing an object. This works on ModelSerializer
        fields and subclasses of ModelSerializers.

        With this function you can pass in serialized objects to foreign key fields
        to generate relationships between objects. 
        """

        # initialize the internal value dictionary
        internal_value = {}

        # iterate over the fields in the serializer
        for field_name, field_serializer in self.fields.items():

            # determine if the field is a ModelSerializer instance
            if isinstance(field_serializer, serializers.ModelSerializer):
                
                # get a reference to the object model class
                field_model = field_serializer.Meta.model

                # if the field exists in the supplied data
                if field_name in data:

                    # set the required property to False
                    # we do this because we are effectively removing the value from 
                    # the data that is passed to the parent method and we want to avoid
                    # false flags - if there was no data supplied to the serializer, 
                    # the required flag won't be changed and will still throw an error
                    field_serializer.required = False

                    # determine the supplied value for the field
                    supplied_value = data.pop(field_name, None)

                    # if the supplied value is None, set the internal value to None
                    if supplied_value == None:
                        internal_value[field_name] = None

                    # if the supplied value is a dictionary, get the corresponding object instance by id
                    elif isinstance(supplied_value, dict):
                        internal_value[field_name] = field_model.objects.get( pk=supplied_value['id'] )

                    # otherwise, we assume the supplied value is the private key for the object instance
                    else:
                        internal_value[field_name] = field_model.objects.get( pk=supplied_value )

        return internal_value

    def to_internal_value(self, data): 

        # make a copy of the data because the data that comes in from an http request
        # is immutable and we are removing the key here
        data = copy.deepcopy(data)    

        # initialize the internal value dictionary
        internal_value = {}

        if self.coerce == True:
            internal_value = self.coerce_foreign_key_values( data )

        # merge the internal_vales from the parent class with those we defined above
        internal_value = { **super().to_internal_value(data), **internal_value }
        return internal_value

    @classmethod
    def add_fields( cls, *fields ):

        cls.Meta.fields = [ *cls.Meta.fields, *fields ]

    @classmethod
    def add_field( cls, name, serializer=None ):

        if serializer:
            setattr(cls, name, serializer)
            cls.add_fields( name )
