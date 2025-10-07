import importlib
import os
import sys
from unittest import TestCase, main
from unittest.mock import patch


BASE_ENV = {
    "API_ID": "12345",
    "API_HASH": "0123456789abcdef0123456789abcdef",
    "BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    "RP_CHANNEL": "0",
}


class IsEnabledTests(TestCase):
    def setUp(self):
        self.info = self._load_info()

    def tearDown(self):
        sys.modules.pop("info", None)

    def _load_info(self, overrides=None):
        env = BASE_ENV.copy()
        if overrides:
            env.update(overrides)
        with patch.dict(os.environ, env, clear=True):
            sys.modules.pop("info", None)
            return importlib.import_module("info")

    def test_truthy_values(self):
        truthy_inputs = [
            True,
            "True",
            "true",
            " yes ",
            "Y",
            "1",
            "enable",
            "ON",
        ]
        for value in truthy_inputs:
            with self.subTest(value=value):
                self.assertTrue(self.info.is_enabled(value, False))

    def test_falsy_values(self):
        falsy_inputs = [
            False,
            "False",
            "false",
            " no ",
            "N",
            "0",
            "disable",
            "Off",
        ]
        for value in falsy_inputs:
            with self.subTest(value=value):
                self.assertFalse(self.info.is_enabled(value, True))

    def test_unknown_values_fall_back_to_default(self):
        self.assertTrue(self.info.is_enabled("maybe", True))
        self.assertFalse(self.info.is_enabled("maybe", False))

    def test_none_falls_back_to_default(self):
        self.assertTrue(self.info.is_enabled(None, True))
        self.assertFalse(self.info.is_enabled(None, False))

    def test_environment_sample_configuration(self):
        sample_caption = (
            "<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <code>{file_name}</code>\n\n"
            "=========== • ✠ • ===========\n"
            "▫️ ɢʀᴏᴜᴘ : </b><b>@CinimaAdholokaam</b> \n"
            "<b>▫️ ᴄʜᴀɴɴᴇʟ : </b><b>@Calinkzz</b>\n"
            "<b>=========== • ✠ • ===========</b>"
        )
        overrides = {
            "ADMINS": "1291364201",
            "API_ID": "2032193",
            "API_HASH": "8e06818e6ca64ab674031280c063b2e1",
            "AUTH_CHANNEL": "-1001802060546",
            "BOT_TOKEN": "5208722762:AAGQmIy-WhZrFJNOj068GwPXf_kYKSNanxk",
            "CACHE_TIME": "100",
            "CHANNELS": "-1001769102299 -1001329116889",
            "COLLECTION_NAME": "channel_files",
            "CUSTOM_FILE_CAPTION": sample_caption,
            "DATABASE_NAME": "gtberno",
            "DATABASE_URI": "mongodb://example",
            "LOG_CHANNEL": "-1001655120387",
            "PICS": "https://telegra.ph/file/2e3e6a526ea4e1f5cde53.jpg",
            "P_TTI_SHOW_OFF": "False",
            "RP_CHANNEL": "-1001527001672",
            "SINGLE_BUTTON": "True",
            "SPELL_CHECK_REPLY": "True",
        }
        info = self._load_info(overrides)

        self.assertEqual(info.API_ID, 2032193)
        self.assertEqual(info.API_HASH, overrides["API_HASH"])
        self.assertEqual(info.BOT_TOKEN, overrides["BOT_TOKEN"])
        self.assertEqual(info.CACHE_TIME, 100)
        self.assertEqual(info.ADMINS, [1291364201])
        self.assertEqual(info.CHANNELS, [-1001769102299, -1001329116889])
        self.assertEqual(info.AUTH_CHANNEL, -1001802060546)
        self.assertFalse(info.P_TTI_SHOW_OFF)
        self.assertTrue(info.SINGLE_BUTTON)
        self.assertTrue(info.SPELL_CHECK_REPLY)
        self.assertEqual(info.RP_CHANNEL, -1001527001672)
        self.assertEqual(info.CUSTOM_FILE_CAPTION, sample_caption)
        self.assertIn("Spell Check Mode Is Enabled", info.LOG_STR)


if __name__ == "__main__":
    main()
