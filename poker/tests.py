import importlib
import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

import thisisus.settings as settings_module


class PokerSessionList23Tests(TestCase):
    def test_session_list_23_has_own_route_and_template(self):
        self.assertEqual(reverse("poker:session_list_23"), "/poker/23_sessions/")

        user_model = get_user_model()
        user = user_model.objects.create_user(username="testuser", password="pass1234")

        client = Client()
        client.force_login(user)
        response = client.get(reverse("poker:session_list_23"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "poker/session_list_23.html")


class AllSessionsChartTests(TestCase):
    def test_all_sessions_chart_handles_empty_session_data_gracefully(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="emptychartuser", password="pass1234")

        client = Client()
        client.force_login(user)
        response = client.get(reverse("poker:all_sessions_chart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No poker sessions recorded yet")

    def test_all_sessions_buyin_cashout_chart_route_renders(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="comparechartuser", password="pass1234")

        client = Client()
        client.force_login(user)
        response = client.get(reverse("poker:all_sessions_buyin_cashout_chart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buy-In vs Cash-Out")
        self.assertContains(response, "Average Buy-In")
        self.assertContains(response, "Average Cash-Out")

    def test_all_sessions_buyin_cashout_chart_shows_individual_sessions(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="individualsessionuser", password="pass1234")

        from poker.models import PokerSession, Casino

        casino = Casino.objects.create(name="Test Casino")
        PokerSession.objects.create(
            player=user,
            casino=casino,
            stakes="1/2",
            date="2026-10-01",
            buy_in=200,
            cash_out=400,
        )
        PokerSession.objects.create(
            player=user,
            casino=casino,
            stakes="1/2",
            date="2026-10-02",
            buy_in=150,
            cash_out=75,
        )

        client = Client()
        client.force_login(user)
        response = client.get(reverse("poker:all_sessions_buyin_cashout_chart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Session Date")
        self.assertContains(response, "Average Buy-In")
        self.assertContains(response, "Average Cash-Out")
        self.assertNotContains(response, "Session Totals")


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
