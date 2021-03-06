"""
Django-Rest-Framework replacement Serializers for rest_framework_encrypted_lookup
"""
from rest_framework import serializers

from .fields import EncryptedLookupRelatedField, EncryptedLookupField, \
    EncryptedLookupHyperlinkedRelatedField
from .settings import encrypted_lookup_settings
from .utils import id_cipher


class EncryptedLookupSerializerMixin(object):
    lookup_field = encrypted_lookup_settings["lookup_field_name"]

    def get_fields(self):
        ret = serializers.ModelSerializer.get_fields(self)

        if self.lookup_field in ret:
            ret[self.lookup_field] = EncryptedLookupField()

        return ret

    @staticmethod
    def get_cipher():
        return id_cipher


class EncryptedLookupModelSerializer(EncryptedLookupSerializerMixin,
                                     serializers.ModelSerializer):
    """
    Encrypted lookup model serializer to be used in place of rest_framework's
    ModelSerializer

    EncryptedLookupModelSerializer represents related models with a
    EncryptedLookupRelatedField and lookup fields with a EncryptedLookupField,
    provided that these fields would be presented by ModelSerializer.
    """

    serializer_related_field = EncryptedLookupRelatedField  # Django Rest Framework 3.0.0
    _related_class = EncryptedLookupRelatedField  # Django Rest Framework 3.0.1


class EncryptedLookupHyperlinkedModelSerializer(EncryptedLookupSerializerMixin,
                                                serializers.HyperlinkedModelSerializer):

    serializer_related_field = EncryptedLookupHyperlinkedRelatedField  # Django Rest Framework 3.0.0
    _related_class = EncryptedLookupHyperlinkedRelatedField  # Django Rest Framework 3.0.1
