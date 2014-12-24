from django.conf import settings

from rest_framework import serializers

from .fields import EncryptedLookupRelatedField, EncryptedLookupField


class EncryptedLookupModelSerializer(serializers.ModelSerializer):
    """
    Encrypted lookup model serializer to be used in place of rest_framework's ModelSerializer

    EncryptedLookupModelSerializer represents related models with a EncryptedLookupRelatedField and lookup fields
    with a EncryptedLookupField, provided that these fields would be presented by ModelSerializer.
    """

    lookup_field = settings.LOOKUP_FIELD

    _related_class = EncryptedLookupRelatedField

    def get_fields(self):

        ret = super(EncryptedLookupModelSerializer, self).get_fields()

        if self.lookup_field in ret:
            ret[self.lookup_field] = EncryptedLookupField()

        return ret