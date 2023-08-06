

## IMPORTANT:

# Ordering of Test classes is as follows
#  class MyTestSuite ( TestCaseMixin, ApiTests, SerializerTests, ModelTests, TestCase ):
#  class MyTestSuite ( TestCaseMixin, ApiMixin, SerializerTests, ModelTests, TestCase ):


from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient


import simplejson as json
from django.utils import timezone
from datetime import timedelta
import datetime
from collections import OrderedDict

from decimal import *


class AgapeTests(object):

    """ Map which defines an instances foreign key fields and the model, serializer, and
    serializer fields to use when creating object representations.
    """
    foreign_key_map = {}

    """ This field is set be each test so that the test is self aware of it's own testing group"""
    test_group = None
    test_label = None

    def sharedSetUp(self):
        e = "You must provide a TestCase mixin which defines your create and update data."
        raise Exception( e )


    def beforeEach(self):
        """ Called before each test """
        pass

    def afterEach(self):
        """ Called after each test """
        pass

    def identify(self, group, label):
        """ Called by each test to identify the current test. This can be used by
        derived classes to modify behavior in the beforeEach and afterEach methods """
        self.test_group = group
        self.test_label = label


    def create_object( self, model, data ):
        instance = model.objects.create(**data)
        return instance


    def create_objects(self, model, data):
        objects = []

        for item in data:
            instance = self.create_object( model, item )
            objects.append( instance )

        return objects


    def create_requisite_objects(self,model,data):

        print("create_requisite_objects() deprecated. Use create_objects() instead.")

        for item in data:
            model.objects.create(**item)

    def transform_foreign_key_to_serialized_data(self, field, key):

        map = self.foreign_key_map[field]
        instance = map['model'].objects.get( pk=key )
        serialized_data = map['serializer']( instance, fields=map['fields'] ).data
        return serialized_data

    def transform_data_to_serialized_data(self, data):
        
        serialized_data = []

        # iterate over each record in the data
        for record in data:

            serialized_record = {}
            
            # and transform each field/value pair as needed
            for field, value in record.items():

                # if the field ends in id, remove the _id portion
                if field.endswith('_id'):
                    field =  field[:-3]

                    # if there is a foreign map defined for this field
                    if field in self.foreign_key_map and not value == None:
                        # inflate the value to a full representation of the object
                        serialized_record[field] = self.transform_foreign_key_to_serialized_data( field, value )

                    else:
                        serialized_record[field] = value

                # if it is a datetime object
                elif isinstance(value, datetime.datetime):
                    # format as a datetime string
                    serialized_record[field] = value.strftime('%Y-%m-%dT%H:%M:%S')

                # if it is a date object
                elif isinstance(value,datetime.date):
                     # format as a date string
                    serialized_record[field] = value.strftime('%Y-%m-%d')

                else:
                    serialized_record[field] = value



            serialized_data.append(serialized_record)

        return serialized_data


    def assertSerializedInstanceEqual(self, serialized_instance, expected_data):

        # compare the response to the expected data
        for key in expected_data.keys():
            instance_value = serialized_instance.get(key)
            expected_value = expected_data[key]

            # if instance value is an ordered dict, convert and perform a dict equal
            if isinstance( instance_value, OrderedDict ):
                instance_value = json.loads(json.dumps(instance_value))

            # if expected value is a dictionary, perform a dict-equal
            if isinstance(expected_value, dict):
                self.assertDictEqual( instance_value, expected_value, "Comparing {} attribute".format(key) )
            
            # if expected value is a decimal, convert testing value to a decimal
            if isinstance(expected_value, Decimal):
                instance_value = Decimal(instance_value)
                self.assertEqual( instance_value, expected_value, "Comparing {} attribute".format(key) )

            # otherwise a normal assert equal
            else:
                self.assertEqual( instance_value, expected_value, "Comparing {} attribute".format(key) )




class TestCaseMixin():
    # *TODO: Should these methods be moved into the `AgapeTests` base class?*
    def sharedSetUp(self):
        pass

    def serializedSetUp(self):

        self.serialized_create_data = self.transform_data_to_serialized_data( self.create_data )
        
        self.serialized_expect_data = self.transform_data_to_serialized_data( self.expect_data )

        self.serialized_update_data = self.transform_data_to_serialized_data( self.update_data )

        self.serialized_update_expect_data = self.transform_data_to_serialized_data( self.update_expect_data )


    def createRequisiteObjects(self):
        pass 




class ModelTests(AgapeTests):

    def setUp(self):
        self.sharedSetUp()
        self.createRequisiteObjects();


    #     self.createRequisiteObjects();

    def test_model_create(self):

        self.identify('model','create')
        self.beforeEach()

        i = 0
        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()

            # compare instance to expected data
            for key in self.expect_data[i].keys():
                instance_value = getattr(instance, key)
                expected_value = self.expect_data[i][key]
                self.assertEqual(instance_value, expected_value, "Comparing {} attribute".format(key) )
            i+=1

        self.afterEach()
        self.identify(None, None)


    def test_model_retrieve(self):

        self.identify('model','retrieve')
        self.beforeEach()

        i = 0

        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()
            instance_id = instance.id
            instance = None

            # retrieve
            instance = self.model.objects.get( id=instance_id )
            self.assertTrue(instance)
        
            # compare instance to expected data
            for key in self.expect_data[i].keys():
                instance_value = getattr(instance, key)
                expected_value = self.expect_data[i][key]
                self.assertEqual(instance_value, expected_value, "Comparing {} attribute".format(key) )
            i+=1

        self.afterEach()
        self.identify(None, None)

    def test_model_update(self):

        self.identify('model','update')
        self.beforeEach()


        i=0
        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()

            # if there is update data for this record, apply it and check it
            if len(self.update_data) > i and self.update_data[i] != None:

                # update the instance
                for key, value in self.update_data[i].items():
                    instance_value = setattr(instance, key, value )

                # save the instance
                instance.save()

                # retrieve the instance
                instance_id = instance.id
                instance = None
                instance = self.model.objects.get(id=instance_id)
            

            
                # compare instance to expected data
                for key in self.update_expect_data[i].keys():
                    instance_value = getattr(instance, key)
                    expected_value = self.update_expect_data[i][key]
                    self.assertEqual(instance_value, expected_value, "Comparing {} attribute".format(key) )

            i+=1

        self.afterEach()
        self.identify(None, None)


    def test_model_delete(self):

        self.identify('model','delete')
        self.beforeEach()


        i=0
        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()
            
            # retrieve the instance
            instance_id = instance.id
            instance = None
            instance = self.model.objects.get(id=instance_id)
            self.assertTrue(instance)

            # delete the instance
            self.model.objects.filter(id=instance_id).delete()
        

            instance = self.model.objects.filter(id=instance_id).all()
            self.assertTrue(not instance)


            i+=1

        self.afterEach()
        self.identify(None, None)

    def test_model_list(self):

        self.identify('model','list')
        self.beforeEach()


        i=0
        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()
            i+=1

        list = self.model.objects.all()
        self.assertEqual(len(list),len(self.create_data))

        self.afterEach()
        self.identify(None, None)



class SerializerTests(AgapeTests):

    def setUp(self):
        self.sharedSetUp()
        self.createRequisiteObjects();
        self.serializedSetUp()
        self.maxDiff = None

    def test_serializer_serialize(self):

        self.identify('serializer','serialize')
        self.beforeEach()

        i=0
        while i < len(self.create_data):
            instance = self.model(**self.create_data[i])
            instance.save()

            serializer = self.serializer_class(instance)

            # compare instance to expected data
            self.assertSerializedInstanceEqual( serializer.data, self.serialized_expect_data[i] )
             
            i+=1

        self.afterEach()
        self.identify(None, None)

    def test_serializer_create(self):

        self.identify('serializer','create')
        self.beforeEach()

        i=0
        while i < len(self.create_data):

            # serializer data is valid
            serializer = self.serializer_class(data=self.serialized_create_data[i])

            self.assertTrue(serializer.is_valid(raise_exception=True), 'Serializer data is valid')

            # create an instance via the serializer
            instance = serializer.create(serializer.validated_data)
            self.assertTrue(instance, 'Created instance from serializer data')
            i+=1


        self.afterEach()
        self.identify(None, None)
        
    def test_serializer_update(self):

        self.identify('serializer','update')
        self.beforeEach()

        i=0
        while i < len(self.create_data):

            instance = self.model(**self.create_data[i])
            instance.save()
            instance_id = instance.id


            # if there is an update for this record, apply it and check it
            if len(self.serialized_update_data) > i and self.serialized_update_data[i] != None:


                serializer = self.serializer_class(instance,data=self.serialized_update_data[i],partial=True)
                self.assertTrue(serializer.is_valid(raise_exception=True), 'Serializer data is valid')

                serializer.update(instance, serializer.validated_data)
                instance.save()

                # verify that the data was updated
                instance = self.model.objects.get(pk=instance_id)
                serializer = self.serializer_class( instance )

                self.assertSerializedInstanceEqual( serializer.data, self.serialized_update_expect_data[i] )

            i+=1

        self.afterEach()
        self.identify(None, None)
                


class ApiMixin():

    def __init__(self, *args, **kwargs):
        self.auth_end_point = '/api/auth/'
        super().__init__( *args, **kwargs )

    def api(self, *path):
        """ Returns a path to an api endpoint
        """
        if path:
            path = list( map( lambda x: str(x), path ) )
            return '{}{}/'.format( self.api_end_point, '/'.join(path) )
        else:
            return self.api_end_point

    def authenticate(self, **kwargs):
        """ Authenticate the mock http session.

            Ex: self.authenticate( username="admin", password="password" )
        """
        response = self.client.post(self.auth_end_point, dict(**kwargs) )

        if response.data.get('token'):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data.get('token'))

        return response

    def deauthenticate(self):
        """ Authenticate the mock http session.

            Ex: self.authenticate( username="admin", password="password" )
        """
        response = self.client.delete( self.auth_end_point )
        self.client.credentials(HTTP_AUTHORIZATION='')
        return response


    def get( self, api_path=None ):

        if api_path == None:
            api_path = self.api()
        else:
            # argument 1 is the api path
            try:
                # as a list
                iter( api_path )
                api_path = self.api( *api_path )
            except TypeError:
                api_path = self.api( api_path )

        return self.client.get( api_path )


    def make_request( self, request, *args ):

        api_path = None
        data = None

        # if we have 1 argument
        if len(args) == 1:
            # api_path is default api path
            api_path = self.api()
            # data is the argument
            data = args[0]

        # if we have 2 arguments
        elif len(args) == 2:

            # argument 1 is the api path
            try:
                # as a list
                iter(args[0])
                api_path = self.api( *args[0] )
            except TypeError:
                # or as a string
                api_path = self.api( args[0] )

            # argument 2 is the data
            data = args[1]

        # number of arguments error
        else:
            raise( Exception("Post accepts 1 or 2 arguments, you supplied {}.".format( len(args) ) ) )

        request_method = getattr( self.client, request )   

        return request_method( api_path, json.dumps(data), content_type='application/json' )


    def patch( self, *args, **kwargs ):
        return self.make_request('patch', *args, **kwargs )


        # response = self.client.patch( api_path, json.dumps(data), content_type='application/json')
        # return response

    def post( self, *args, **kwargs ):

        return self.make_request('post', *args, **kwargs )

    def delete( self, *args, **kwargs ):

        return self.make_request('delete', *args, **kwargs )


    # def post( self, *args ):

    #     api_path = None
    #     data = None

    #     # if we have 1 argument
    #     if len(args) == 1:
    #         # api_path is default api path
    #         api_path = self.api()
    #         # data is the argument
    #         data = args[0]

    #     # if we have 2 arguments
    #     elif len(args) == 2:

    #         # argument 1 is the api path
    #         try:
    #             # as a list
    #             iter(args[0])
    #             api_path = self.api( *args[0] )
    #         except TypeError:
    #             # or as a string
    #             api_path = args[0]

    #         # argument 2 is the data
    #         data = args[1]

    #     # number of arguments error
    #     else:
    #         raise( Exception("Post accepts 1 or 2 arguments, you supplied {}.".format( len(args) ) ) )



    #     response = self.client.post( api_path, json.dumps(data), content_type='application/json')
    #     return response



class ApiTests(ApiMixin, AgapeTests):
    """  Perform basic testing of basic CRUD and List operations on the api endpoint.

    """

    def setUp(self):
        self.auth_end_point = '/api/auth/'
        self.sharedSetUp()
        self.createRequisiteObjects();
        self.serializedSetUp()
        self.maxDiff = None
        self.client =  APIClient()


    def test_api_create(self):
        """ Test Create
        
        Test the API Endpoint for the ability to create items.
        """

        self.identify('api','create')
        self.beforeEach()

        i=0
        while i < len(self.serialized_create_data):

            create_data = self.serialized_create_data[i]

            # TODO: This should use self.post()
            # the actual post here is done with a json.dumps because the default 
            # http client
            # does not actually serialize the nested objects, so we dump to a json string
            # which the default viewset handles just fine
            response = self.client.post( self.api_end_point, json.dumps(create_data), content_type='application/json' )
            
            # if we did not get a 201 response, display the error for the user
            try:
                self.assertEqual(response.status_code, 201, "Created new instance")
            except Exception as e:
                print(response.data)
                raise e


            # verify the response data
            self.assertSerializedInstanceEqual( response.data, self.serialized_expect_data[i] )

            # verify actual database record was created
            instance = self.model.objects.get(id=response.data.get('id'))
            self.assertTrue(instance)

            i+=1

        self.afterEach()
        self.identify(None, None)
        

    def test_api_retrieve(self):
        """ Test Retrieve
        
        Test the API Endpoint for the ability to retrieve items.
        """

        self.identify('api','retrieve')
        self.beforeEach()

        i=0
        while i < len(self.create_data):

            # creat the object
            instance = self.model( **self.create_data[i] )
            instance.save()

            # remember the item id
            instance_id = instance.id

            # retrieve the item via the api endpoint
            uri = "{}{}/".format(self.api_end_point,instance_id)
            # TODO: This should use self.get()
            response = self.client.get(uri)
            self.assertEqual(response.status_code, 200, "Retrieved")

            # verify the response data
            self.assertSerializedInstanceEqual( response.data, self.serialized_expect_data[i] )

            i+=1


        self.afterEach()
        self.identify(None, None)
        
    def test_api_update(self):

        self.identify('api','update')
        self.beforeEach()

        i=0
        while i < len(self.update_data):

            # creat the object
            instance = self.model( **self.create_data[i] )
            instance.save()

            # remember the item id
            instance_id = instance.id

            # perform the update via the api endpoint
            update_data = self.serialized_update_data[i]
            uri = "{}{}/".format(self.api_end_point,instance_id)

            # TODO: This should use self.patch()
            response = self.client.patch(uri, json.dumps(update_data), content_type='application/json')
            try:
                self.assertEqual(response.status_code, 200, "Updated instance")
            except Exception as e:
                print(response.data)
                raise e
            

            # retrieve the item via the api endpoint
            response = None
            response = self.client.get(uri)

            # verify the response data
            self.assertSerializedInstanceEqual( response.data, self.serialized_update_expect_data[i] )


            i+=1

        self.afterEach()
        self.identify(None, None)
        
    def test_api_delete(self):

        self.identify('api','delete')
        self.beforeEach()
        
        i=0
        while i < len(self.create_data):

            # creat the object to test
            instance = self.model( **self.create_data[i] )
            instance.save()

            # remember the item id
            instance_id = instance.id

            # perform delete via the api endpoint
            uri = "{}{}/".format(self.api_end_point,instance_id)

            # TODO: This should use self.delete()
            response = self.client.delete( uri )    
            self.assertEqual(response.status_code, 204, "Deleted instance")

            # retrieve the item via the api endpoint
            response = None
            response = self.client.get(uri)
            self.assertEqual(response.status_code, 404, "Instance not found")


            i+=1

        self.afterEach()
        self.identify(None, None)
        
    def test_api_list(self):

        self.identify('api','list')
        self.beforeEach()

        i=0
        while i < len(self.create_data):

            # create the item to test
            instance = self.model( **self.create_data[i] )
            instance.save()

            i+=1

        response = None

        # TODO: This should use self.get()
        response = self.client.get(self.api_end_point)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.create_data))         
   

        self.afterEach()
        self.identify(None, None)
        


# The test suite must inherit these classes in this order, as the setUp() method must be inherited
# from the ApiTests class.

class TestSuite( TestCaseMixin, ApiTests, SerializerTests, ModelTests ):
    """ A class which combines the ApiTests, SerializerTests, and ModelTests classes. Also inherits from
    the TestCaseMixin.

    Derive your test cases from this class when creating standard app models that have api endpoints.
    """
    pass
