import json
import sys

from django.test import TestCase
from django.db import models

from rest_framework_encrypted_lookup.utils import id_cipher, IDCipher
from rest_framework_encrypted_lookup.fields import EncryptedLookupRelatedField, EncryptedLookupField
from rest_framework_encrypted_lookup.serializers import EncryptedLookupModelSerializer

# In Django, defining a model induces side effects such as database table creation.
# To avoid these side effects during non-test runs, before we define models we first
# must determine whether this is a test...
if 'runtests.py' in sys.argv[0] or (len(sys.argv) >= 3 and sys.argv[1:2] == ['test']):
    # and if so, we declare dummy models/querysets that we will use for testing.
    class DummyModel0(models.Model):
        pass

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

    dummy_queryset = DummyQueryset()

    class DummySerializer(EncryptedLookupModelSerializer):

        class Meta:
            model = DummyModel
            fields = ['id', 'related']


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

        # Assert that EncryptedLookupField.to_representation gives an encrypted
        # representation of an integer value.
        self.assertEqual(id_cipher.encode(1), field.to_representation(1))

    def test_encrypted_lookup_related_field(self):

        dummy_object = dummy_queryset.get(pk=1)

        field = EncryptedLookupRelatedField(queryset=dummy_queryset)

        # Assert that to_internal_value and to_representation are inverse functions
        self.assertEqual(dummy_object, field.to_internal_value(json.dumps(field.to_representation(dummy_object))))


class ModelSerializerTests(TestCase):

    def test_model_serializer(self):

        serializer = DummySerializer()

        # Assert that our lookup field is an encrypted lookup field
        self.assertIsInstance(serializer.get_fields()['id'], EncryptedLookupField)

        # Assert that our related field is an encrypted lookup related field
        self.assertIsInstance(serializer.get_fields()['related'], EncryptedLookupRelatedField)
