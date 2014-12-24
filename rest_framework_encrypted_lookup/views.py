from rest_framework import viewsets

from .utils import id_cipher


class EncryptedLookupGenericViewSet(viewsets.GenericViewSet):
    """
    GenericViewSet subclass capable of decrypting our encrypted lookup field references.

    Dispatch method looks for lookup_field references from the url string arguments,
    replaces them with decrypted values, and calls super's dispatch with the results.
    """

    def dispatch(self, request, *args, **kwargs):

            lookup = kwargs.get(self.lookup_field, None)

            if lookup is not None:
                kwargs[self.lookup_field] = id_cipher.decode(lookup)

            return super(EncryptedLookupGenericViewSet, self).dispatch(request, *args, **kwargs)