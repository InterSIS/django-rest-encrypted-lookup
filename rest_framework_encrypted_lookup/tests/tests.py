import json
import sys


from django.test import TestCase
from django.db import models
from django.http import Http404

from rest_framework.test import APIRequestFactory
from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_encrypted_lookup.utils import id_cipher, IDCipher
from rest_framework_encrypted_lookup.fields import EncryptedLookupRelatedField, EncryptedLookupField, \
    EncryptedLookupHyperlinkedRelatedField
from rest_framework_encrypted_lookup.serializers import EncryptedLookupModelSerializer, \
    EncryptedLookupHyperlinkedModelSerializer
from rest_framework_encrypted_lookup.views import EncryptedLookupGenericViewSet

# In Django, defining a model induces side effects such as database table creation.
# To avoid these side effects during non-test runs, before we define models we first
# must determine whether this is a test...
if 'runtests.py' in sys.argv[0] or (len(sys.argv) >= 3 and sys.argv[1:2] == ['test']):

    class DummyModel0(models.Model):
        text = models.TextField(blank=True, null=True)

    class DummyModel(models.Model):

        related = models.ForeignKey(DummyModel0)

        def __init__(self, *args, **kwargs):
            super(DummyModel, self).__init__(*args, **kwargs)

            self.pk = kwargs['pk']

    # Our "database" of dummy objects:
    dummy_objects = [DummyModel(pk=i) for i in range(0, 10)]

    # A queryset class to retrieve dummy objects:
    class DummyQueryset(object):

        def get(self, pk):
            return dummy_objects[pk]

        def __iter__(self, *args, **kwargs):
            return dummy_objects.__iter__(*args, **kwargs)

    dummy_queryset = DummyQueryset()

    class DummySerializer(EncryptedLookupModelSerializer):

        class Meta:
            model = DummyModel
            fields = ['id', 'related']

    class HyperlinkedDummySerializer(EncryptedLookupHyperlinkedModelSerializer):

        class Meta:
            model = DummyModel
            fields = ['id', 'related']

    class DummyView(EncryptedLookupGenericViewSet,
                    viewsets.mixins.ListModelMixin):

        queryset = dummy_queryset
        serializer_class = DummySerializer

        def retrieve(self, request, *args, **kwargs):
            instance = dummy_objects[kwargs['pk']]
            serializer = self.get_serializer(instance)
            return Response(serializer.data)



class IDCipherTests(TestCase):

    def test_decryption(self):

        # Assert successful encryption and decryption for several numbers within
        # the IntegerField range.
        for i in range(1, 10000):
            self.assertEqual(i, id_cipher.decode(id_cipher.encode(i)))

        for i in range(-2147483648, -2147453648):
            self.assertEqual(i, id_cipher.decode(id_cipher.encode(i)))

        for i in range(2147453647, 2147483647):
            self.assertEqual(i, id_cipher.decode(id_cipher.encode(i)))

    def test_secret_key_provision(self):
        new_id_cipher = IDCipher(secret="blabla&&;;asdfblaasdf")
        for i in range(-10, 10):
            self.assertEqual(i, new_id_cipher.decode(new_id_cipher.encode(i)))


class FieldTests(TestCase):

    def test_encrypted_lookup_field(self):

        field = EncryptedLookupField()

        serializer = DummySerializer()
        field.bind("field_name", serializer)

        # Assert that EncryptedLookupField.to_representation gives an encrypted
        # representation of an integer value.
        self.assertEqual(id_cipher.encode(1), field.to_representation(1))

    def test_encrypted_lookup_related_field(self):

        dummy_object = dummy_queryset.get(pk=1)

        field = EncryptedLookupRelatedField(queryset=dummy_queryset)
        serializer = DummySerializer()
        field.bind("field_name", serializer)

        # Assert that to_internal_value and to_representation are inverse functions
        self.assertEqual(dummy_object, field.to_internal_value(json.dumps(field.to_representation(dummy_object))))

    def test_encrypted_lookup_hyperlinked_related_field(self):

        dummy_object = dummy_queryset.get(pk=1)

        field = EncryptedLookupHyperlinkedRelatedField("viewname", queryset=dummy_queryset)

        serializer = DummySerializer()
        serializer._context = {"request": "a request"}
        field.bind("field_name", serializer)

        field.reverse = lambda view_name, kwargs, request, format: json.dumps(kwargs)

        # Assert that get_url encodes the object pk
        self.assertIn(id_cipher.encode(1), field.get_url(dummy_object, "viewname", {}, ""))

        # Assert that DRF's to_representation makes use of our encryption methods
        self.assertIn(id_cipher.encode(1), field.to_representation(dummy_object))

        # field.resolve = lambda data: Namespace(view_name="viewname", args=(), kwargs={"pk": data})

        # Assert that get_object decodes an encoded lookup to return the correct object
        self.assertEqual(dummy_object, field.get_object("", (), {"pk": id_cipher.encode(1)}))

        # Assert that DRF's to_internal_value makes use of our decryption methods
        self.assertEqual(dummy_object, field.to_internal_value("https://test/" + id_cipher.encode(1) + '/'))


class SerializerTests(TestCase):

    def test_model_serializer(self):

        serializer = DummySerializer()

        # Assert that our lookup field is an encrypted lookup field
        self.assertIsInstance(serializer.get_fields()['id'], EncryptedLookupField)

        # Assert that our related field is an encrypted lookup related field
        self.assertIsInstance(serializer.get_fields()['related'], EncryptedLookupRelatedField)

    def test_hyperlinked_model_serializer(self):

        serializer = HyperlinkedDummySerializer()

        # Assert that our lookup field is an encrypted lookup field
        self.assertIsInstance(serializer.get_fields()['id'], EncryptedLookupField)

        # Assert that our related field is an encrypted lookup related field
        self.assertIsInstance(serializer.get_fields()['related'], EncryptedLookupHyperlinkedRelatedField)

    def test_independent_by_serializer_ciphers(self):
        """
        Fields should use the cipher provided by their parent serializer.
        """

        first_field = EncryptedLookupField()
        first_serializer = DummySerializer()
        first_serializer.get_cipher = lambda: IDCipher(secret="first")
        first_field.bind("field_name", first_serializer)

        second_field = EncryptedLookupField()
        second_serializer = DummySerializer()
        second_serializer.get_cipher = lambda: IDCipher(secret="second")
        second_field.bind("field_name", second_serializer)

        # Assert that the two fields do not encrypt to the same value.
        self.assertNotEqual(second_field.to_representation(1), first_field.to_representation(1))

        # Assert that the fields encrypt to the same value as new ciphers given the same secrets
        self.assertEqual(IDCipher(secret="first").encode(1), first_field.to_representation(1))
        self.assertEqual(IDCipher(secret="second").encode(1), second_field.to_representation(1))


factory = APIRequestFactory()


class ViewTests(TestCase):

    def test_view_dispatch_decryption(self):

        DummyView.get_object = lambda request, *args, **kwargs: dummy_objects[kwargs['pk']]
        view = DummyView.as_view({'get': 'retrieve', })

        request = factory.get('/' + IDCipher().encode(1), format='json')
        DummyView.request = request
        DummyView.format_kwarg = "json"
        response = view(request, pk=IDCipher().encode(1)).render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ErrorTests(TestCase):

    def test_base32_decode_lookup_raises_404(self):

        DummyView.get_object = lambda request, *args, **kwargs: dummy_objects[kwargs['pk']]
        view = DummyView.as_view({'get': 'retrieve', })
        request = factory.get('/' + "1", format='json')
        DummyView.request = request
        DummyView.format_kwarg = "json"

        with self.assertRaises(Http404):
            view(request, pk="1").render()



