from rest_framework import serializers

from .fields import EncryptedLookupRelatedField, EncryptedLookupField
from .settings import encrypted_lookup_settings


class EncryptedLookupModelSerializer(serializers.ModelSerializer):
    """
    Encrypted lookup model serializer to be used in place of rest_framework's ModelSerializer

    EncryptedLookupModelSerializer represents related models with a EncryptedLookupRelatedField and lookup fields
    with a EncryptedLookupField, provided that these fields would be presented by ModelSerializer.
    """

    lookup_field = encrypted_lookup_settings["lookup_field_name"]

    serializer_related_field = EncryptedLookupRelatedField  # Django Rest Framework 3.0.0
    _related_class = EncryptedLookupRelatedField  # Django Rest Framework 3.0.1

    def get_fields(self):

        ret = super(EncryptedLookupModelSerializer, self).get_fields()

        if self.lookup_field in ret:
            ret[self.lookup_field] = EncryptedLookupField()

        return ret