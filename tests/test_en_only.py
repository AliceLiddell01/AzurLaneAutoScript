import json
import unittest
from pathlib import Path

from module.config.config_updater import ConfigUpdater
from module.config.server import EN_PACKAGE, to_package, to_server

ROOT = Path(__file__).resolve().parents[1]


class EnOnlyServerTests(unittest.TestCase):
    def test_en_values(self):
        self.assertEqual(to_server("auto"), "en")
        self.assertEqual(to_server("en"), "en")
        self.assertEqual(to_server(EN_PACKAGE), "en")
        self.assertEqual(to_package("en"), EN_PACKAGE)

    def test_removed_clients_are_rejected(self):
        for package in ("com.YoStarJP.AzurLane", "com.bilibili.azurlane", "com.hkmanjuu.azurlane.gp"):
            with self.subTest(package=package):
                with self.assertRaisesRegex(ValueError, "Unsupported client: EN-only fork"):
                    to_server(package)

    def test_generated_options_are_en_only(self):
        args = json.loads((ROOT / "module/config/argument/args.json").read_text(encoding="utf-8"))
        self.assertEqual(args["Alas"]["Emulator"]["PackageName"]["option"], ["auto", EN_PACKAGE])
        server_options = args["Alas"]["Emulator"]["ServerName"]["option"]
        self.assertEqual(server_options[0], "disabled")
        self.assertTrue(all(v == "disabled" or v.startswith("en-") for v in server_options))

    def test_old_package_migrates_to_auto(self):
        old = {"Alas": {"Emulator": {"PackageName": "com.YoStarJP.AzurLane"}}}
        new = ConfigUpdater().config_update(old)
        self.assertEqual(new["Alas"]["Emulator"]["PackageName"], "auto")

    def test_only_english_locale_bundle_exists(self):
        locales = sorted(p.name for p in (ROOT / "module/config/i18n").glob("*.json"))
        self.assertEqual(locales, ["en-US.json"])

    def test_removed_asset_trees_are_absent(self):
        for server in ("cn", "jp", "tw"):
            self.assertFalse((ROOT / "assets" / server).exists())

    def test_azurstats_integration_is_absent(self):
        self.assertFalse((ROOT / "module/statistics/azurstats.py").exists())
        self.assertTrue((ROOT / "module/statistics/drop_record.py").exists())
        args = json.loads((ROOT / "module/config/argument/args.json").read_text(encoding="utf-8"))
        drop = args["Alas"]["DropRecord"]
        self.assertNotIn("AzurStatsID", drop)
        self.assertNotIn("API", drop)
        for name, value in drop.items():
            if name == "SaveFolder":
                continue
            self.assertEqual(value.get("option", []), ["do_not", "save"])

    def test_old_upload_modes_migrate_safely(self):
        old = {"Alas": {"DropRecord": {
            "ResearchRecord": "save_and_upload",
            "CommissionRecord": "upload",
        }}}
        new = ConfigUpdater().config_update(old)
        self.assertEqual(new["Alas"]["DropRecord"]["ResearchRecord"], "save")
        self.assertEqual(new["Alas"]["DropRecord"]["CommissionRecord"], "do_not")


if __name__ == "__main__":
    unittest.main()
