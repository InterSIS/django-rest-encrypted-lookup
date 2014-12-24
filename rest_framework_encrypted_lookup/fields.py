import json

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .utils import id_cipher


class EncryptedLookupField(serializers.ReadOnlyField):
    """
    Read-only rest_framework field used to present an encrypted-lookup field.
    """
    def to_representation(self, value):
        return id_cipher.encode(value)


class EncryptedLookupRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Encrypted lookup field to be used in place of PrimaryKeyRelatedField
    """

    def to_internal_value(self, data):
        try:
            if isinstance(data, str):
                data = json.loads(data)
            data = id_cipher.decode(data)
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type_encrypted_lookup', data_type=type(data).__name__)

    def to_representation(self, value):
        return id_cipher.encode(value.pk)

EncryptedLookupRelatedField.default_error_messages['incorrect_type_encrypted_lookup'] = \
    _('Incorrect type. Expected string value, received {data_type}.')