EXTRA_REQUIRED_SETTINGS = ('secret_key', )

default_encrypted_lookup_settings = {
    'lookup_field_name': 'pk',
}

try:
    from django.conf import settings
    encrypted_lookup_settings = getattr(settings, 'ENCRYPTED_LOOKUP')
except AttributeError:
    raise AttributeError("Django.conf.settings must include an ENCRYPTED_LOOKUP settings dictionary.")
else:
    for required_key in EXTRA_REQUIRED_SETTINGS:
        if required_key not in encrypted_lookup_settings:
            raise AttributeError("ENCRYPTED_LOOKUP settings dictionary must include a '%s' key." % required_key)

    for key in encrypted_lookup_settings:
        if key not in default_encrypted_lookup_settings and key not in EXTRA_REQUIRED_SETTINGS:
            raise AttributeError("Unrecognized ENCRYPTED_LOOKUP setting key: '%s'" % key)

    for key, value in default_encrypted_lookup_settings.items():
        if key not in encrypted_lookup_settings:
            encrypted_lookup_settings[key] = value