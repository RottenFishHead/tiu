import importlib
import os
from unittest import mock

from django.test import SimpleTestCase

import thisisus.settings as settings_module


class PlayerProfileStorageSettingsTests(SimpleTestCase):
    def test_default_storage_falls_back_to_local_filesystem_when_r2_is_unconfigured(self):
        original_env = {key: os.environ.get(key) for key in (
            "R2_ACCOUNT_ID",
            "R2_BUCKET_NAME",
            "R2_ACCESS_KEY_ID",
            "R2_SECRET_ACCESS_KEY",
        )}

        try:
            with mock.patch.dict(
                os.environ,
                {
                    "R2_ACCOUNT_ID": "",
                    "R2_BUCKET_NAME": "",
                    "R2_ACCESS_KEY_ID": "",
                    "R2_SECRET_ACCESS_KEY": "",
                },
                clear=False,
            ):
                importlib.reload(settings_module)
                self.assertEqual(
                    settings_module.STORAGES["default"]["BACKEND"],
                    "django.core.files.storage.FileSystemStorage",
                )
        finally:
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            importlib.reload(settings_module)
