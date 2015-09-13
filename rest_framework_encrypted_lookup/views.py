"""
Django-Rest-Framework replacement Views for rest_framework_encrypted_lookup
"""
import binascii

from django.http import Http404

from rest_framework import viewsets


class EncryptedLookupGenericViewSet(viewsets.GenericViewSet):
    """
    GenericViewSet subclass capable of decrypting our encrypted lookup field
    references.

    Dispatch method looks for lookup_field references from the url string
    arguments, replaces them with decrypted values, and calls super's dispatch
    with the results.
    """

    def __init__(self):
        self.request = None
        self.format_kwarg = None

        super(EncryptedLookupGenericViewSet, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        lookup = kwargs.get(self.lookup_field, None)

        if lookup is not None:
            # Pre-set some of the variables which may be needed to resolve
            # serializer context:
            self.request = request
            self.format_kwarg = self.get_format_suffix(**kwargs)

            try:
                kwargs[self.lookup_field] = self.get_serializer().get_cipher().decode(lookup)
            except binascii.Error:  # Python 3
                raise Http404
            except TypeError:       # Python 2
                raise Http404

        return super(EncryptedLookupGenericViewSet, self).dispatch(request, *args, **kwargs)
