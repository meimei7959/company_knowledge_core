import unittest

from scripts.validate_desktop_native_proof import ROOT, validate


class DesktopNativeProofTests(unittest.TestCase):
    def test_native_proof_artifacts_validate(self):
        self.assertEqual(validate(ROOT), [])

    def test_manifest_preserves_exact_toolchain_blocker(self):
        manifest = ROOT.joinpath(
            "projects/company-knowledge-core/desktop-native-proof/native-proof-manifest.json"
        ).read_text(encoding="utf-8")
        self.assertIn("rustc", manifest)
        self.assertIn("cargo", manifest)
        self.assertIn("spawnSync rustc ENOENT", manifest)
        self.assertIn("real-native-tauri-v2-proof-blocked", manifest)
        self.assertIn("Do not unlock real native proof testing", manifest)

    def test_scaffold_uses_tauri_v2_not_electron(self):
        package_json = ROOT.joinpath(
            "projects/company-knowledge-core/desktop-native-proof/package.json"
        ).read_text(encoding="utf-8")
        cargo_toml = ROOT.joinpath(
            "projects/company-knowledge-core/desktop-native-proof/src-tauri/Cargo.toml"
        ).read_text(encoding="utf-8")
        self.assertIn("@tauri-apps/cli", package_json)
        self.assertIn('tauri = { version = "2"', cargo_toml)
        self.assertNotIn("electron", package_json.lower())


if __name__ == "__main__":
    unittest.main()
