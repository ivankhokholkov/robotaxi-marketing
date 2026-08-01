from __future__ import annotations

import base64
import pathlib
import subprocess
import sys
import tempfile
import unittest


БАННЕРЫ = pathlib.Path(__file__).resolve().parents[1]
НОВАЯ = БАННЕРЫ / "новая-кампания.py"
СОХРАНИТЬ = БАННЕРЫ / "сохранить-imagegen.py"


class CampaignToolsTest(unittest.TestCase):
    def test_create_campaign_in_each_result_section_and_refuse_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "robotaxi-marketing"
            sections = {
                "ads": "04_реклама",
                "content": "06_контент",
                "visuals": "07_визуалы",
            }
            for campaign_type, section in sections.items():
                with self.subTest(campaign_type=campaign_type):
                    slug = f"тест-{campaign_type}"
                    cmd = [
                        sys.executable,
                        str(НОВАЯ),
                        "--type",
                        campaign_type,
                        "--slug",
                        slug,
                        "--style",
                        "kinetic-moscow",
                        "--date",
                        "2026-08-01",
                        "--root",
                        str(root),
                    ]
                    first = subprocess.run(cmd, text=True, capture_output=True)
                    self.assertEqual(first.returncode, 0, first.stderr)

                    campaign = root / "РЕЗУЛЬТАТЫ" / section / f"2026-08-01_{slug}"
                    self.assertTrue((campaign / "00_BRIEF.md").is_file())
                    self.assertTrue((campaign / "01_REFERENCES/README.md").is_file())
                    self.assertTrue((campaign / "02_PROMPTS").is_dir())
                    self.assertTrue((campaign / "03_RAW/rejected").is_dir())
                    self.assertTrue((campaign / "04_FINAL").is_dir())
                    self.assertTrue((campaign / "05_QA/QA.md").is_file())
                    self.assertTrue((campaign / "MANIFEST.yaml").is_file())
                    manifest = (campaign / "MANIFEST.yaml").read_text()
                    self.assertIn('style_id: "kinetic-moscow"', manifest)
                    self.assertIn("Kinetic Moscow", manifest)
                    self.assertIn("REFERENCE-CONTACT-SHEET.png", manifest)
                    reference_readme = (campaign / "01_REFERENCES/README.md").read_text()
                    self.assertIn("СТИЛЬ-Kinetic-Moscow.md", reference_readme)
                    self.assertIn("social-1080x1350", reference_readme)

                    second = subprocess.run(cmd, text=True, capture_output=True)
                    self.assertNotEqual(second.returncode, 0)
                    self.assertIn("уже существует", second.stderr)

    def test_save_imagegen_result_versions_existing_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            campaign = root / "campaign"
            (campaign / "03_RAW/rejected").mkdir(parents=True)
            (campaign / "01_REFERENCES").mkdir()
            (campaign / "04_FINAL").mkdir()
            (campaign / "00_BRIEF.md").write_text("# brief\n")

            source = root / "generated.png"
            source.write_bytes(
                base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9WlS8AAAAASUVORK5CYII="
                )
            )

            cmd = [
                sys.executable,
                str(СОХРАНИТЬ),
                "--source",
                str(source),
                "--campaign",
                str(campaign),
                "--name",
                "01_anchor.png",
                "--stage",
                "raw",
            ]
            first = subprocess.run(cmd, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((campaign / "03_RAW/01_anchor.png").is_file())

            second = subprocess.run(cmd, text=True, capture_output=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertTrue((campaign / "03_RAW/01_anchor-v2.png").is_file())
            self.assertTrue((campaign / "IMPORTS.md").is_file())

    def test_save_imagegen_rejects_misleading_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            campaign = root / "campaign"
            campaign.mkdir()
            (campaign / "00_BRIEF.md").write_text("# brief\n")

            source = root / "generated.png"
            source.write_bytes(
                base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9WlS8AAAAASUVORK5CYII="
                )
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(СОХРАНИТЬ),
                    "--source",
                    str(source),
                    "--campaign",
                    str(campaign),
                    "--name",
                    "01_anchor.jpg",
                    "--stage",
                    "raw",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("не совпадает", result.stderr)
            self.assertFalse((campaign / "03_RAW/01_anchor.jpg").exists())


if __name__ == "__main__":
    unittest.main()
