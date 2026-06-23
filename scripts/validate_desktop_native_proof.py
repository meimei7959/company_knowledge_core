"""Validate AI Native OS desktop native proof artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "projects" / "company-knowledge-core" / "desktop-native-proof"

REQUIRED_EVIDENCE_IDS = {
    "mac-packaging",
    "windows-packaging",
    "signing-notarization",
    "updater-channel",
    "secure-storage",
    "deep-link",
    "notifications",
    "enterprise-proxy-network",
    "runner-pairing-token-flow",
}

FORBIDDEN_SECRET_PATTERNS = [
    re.compile(r"APPLE_PASSWORD\\s*[:=]\\s*['\\\"][^'\\\"]+", re.I),
    re.compile(r"TAURI_SIGNING_PRIVATE_KEY\\s*[:=]\\s*['\\\"][^'\\\"]+", re.I),
    re.compile(r"WINDOWS_PFX_PASSWORD\\s*[:=]\\s*['\\\"][^'\\\"]+", re.I),
    re.compile(r"certificateThumbprint\\s*\"\\s*:\\s*\"[A-Fa-f0-9]{20,}\""),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_manifest(manifest: dict) -> list[str]:
    problems: list[str] = []
    decision = manifest.get("runtimeDecision") or {}
    if decision.get("preferredRuntime") != "tauri-v2":
        problems.append("manifest: preferredRuntime must be tauri-v2")
    if decision.get("decision") != "real-native-tauri-v2-proof-blocked":
        problems.append("manifest: decision must explicitly record real native proof blocker")
    if decision.get("electronFallbackRequested") is not True:
        problems.append("manifest: Electron fallback decision request must be true when Tauri proof is blocked")
    probe = manifest.get("localEnvironmentProbe") or {}
    for key in ["node", "npm", "rustc", "cargo", "cargoTauri", "npmTauriOffline", "codesigningIdentities", "signingEnv", "windowsRunner", "realProductFrontend", "blocker"]:
        if not probe.get(key):
            problems.append(f"manifest.localEnvironmentProbe: missing {key}")
    if "missing" not in str(probe.get("rustc", "")) or "missing" not in str(probe.get("cargo", "")):
        problems.append("manifest: rustc/cargo blocker must be exact")

    evidence = manifest.get("evidence")
    if not isinstance(evidence, list):
        return problems + ["manifest: evidence must be a list"]
    ids = {str(item.get("id")) for item in evidence}
    missing = REQUIRED_EVIDENCE_IDS - ids
    if missing:
        problems.append(f"manifest: missing evidence ids {sorted(missing)}")
    for item in evidence:
        item_id = item.get("id", "<missing>")
        if not item.get("surface") or not item.get("status") or not item.get("proof"):
            problems.append(f"manifest evidence {item_id}: surface/status/proof required")
        if not item.get("boundary"):
            problems.append(f"manifest evidence {item_id}: boundary required")
        for ref in item.get("artifactRefs", []):
            if not (ARTIFACT_DIR / ref).exists():
                problems.append(f"manifest evidence {item_id}: missing artifact ref {ref}")

    unlock = manifest.get("testUnlock") or {}
    if unlock.get("canUnlockKtAiNativeOsTestDesktopNativeProof") is not False:
        problems.append("manifest: real native proof test unlock must be explicit false")
    if "Do not unlock real native proof testing" not in str(unlock.get("unlockScope", "")):
        problems.append("manifest: unlock scope must block real native proof test")
    return problems


def validate_package(package_json: dict) -> list[str]:
    problems: list[str] = []
    deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
    for dep in [
        "@tauri-apps/cli",
        "@tauri-apps/api",
        "@tauri-apps/plugin-updater",
        "@tauri-apps/plugin-stronghold",
        "@tauri-apps/plugin-deep-link",
        "@tauri-apps/plugin-notification",
    ]:
        if dep not in deps or not str(deps[dep]).startswith("^2"):
            problems.append(f"package.json: {dep} must be declared as Tauri v2 dependency")
    scripts = package_json.get("scripts", {})
    for script in ["tauri:build:mac", "tauri:build:windows", "tauri:signer:generate"]:
        if script not in scripts:
            problems.append(f"package.json: missing {script}")
    return problems


def validate_tauri_conf(conf: dict) -> list[str]:
    problems: list[str] = []
    if conf.get("$schema") != "https://schema.tauri.app/config/2":
        problems.append("tauri.conf.json: schema must be Tauri v2")
    targets = set(((conf.get("bundle") or {}).get("targets") or []))
    for target in ["dmg", "app", "nsis", "msi"]:
        if target not in targets:
            problems.append(f"tauri.conf.json: missing bundle target {target}")
    if (conf.get("bundle") or {}).get("createUpdaterArtifacts") is not True:
        problems.append("tauri.conf.json: createUpdaterArtifacts must be true")
    plugins = conf.get("plugins") or {}
    if "updater" not in plugins:
        problems.append("tauri.conf.json: updater plugin config required")
    if "deep-link" not in plugins:
        problems.append("tauri.conf.json: deep-link plugin config required")
    if "NATIVE_PROOF_REPLACE_WITH_TAURI_SIGNER_PUBLIC_KEY" not in str(plugins.get("updater", {}).get("pubkey", "")):
        problems.append("tauri.conf.json: updater pubkey placeholder must avoid fake secret")
    windows = (conf.get("bundle") or {}).get("windows") or {}
    if windows.get("digestAlgorithm") != "sha256":
        problems.append("tauri.conf.json: Windows digestAlgorithm sha256 required")
    if windows.get("certificateThumbprint"):
        problems.append("tauri.conf.json: certificateThumbprint must not be stored in proof")
    return problems


def validate_rust_sources(cargo: str, lib_rs: str, capabilities: dict) -> list[str]:
    problems: list[str] = []
    for dep in [
        "tauri = { version = \"2\"",
        "tauri-plugin-updater = \"2\"",
        "tauri-plugin-stronghold = \"2\"",
        "tauri-plugin-deep-link = \"2\"",
        "tauri-plugin-notification = \"2\"",
    ]:
        if dep not in cargo:
            problems.append(f"Cargo.toml: missing {dep}")
    for snippet in [
        "tauri_plugin_deep_link::init()",
        "tauri_plugin_notification::init()",
        "tauri_plugin_updater::Builder::new().build()",
        "tauri_plugin_stronghold::Builder::with_argon2",
        "pairing_token_flow_contract",
        "register_all()",
    ]:
        if snippet not in lib_rs:
            problems.append(f"lib.rs: missing {snippet}")
    permissions = set(capabilities.get("permissions") or [])
    for permission in ["updater:default", "stronghold:default", "deep-link:allow-register", "notification:default"]:
        if permission not in permissions:
            problems.append(f"capabilities/default.json: missing {permission}")
    return problems


def validate_no_secrets() -> list[str]:
    problems: list[str] = []
    for path in ARTIFACT_DIR.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".toml", ".rs", ".md"}:
            text = read(path)
            for pattern in FORBIDDEN_SECRET_PATTERNS:
                if pattern.search(text):
                    problems.append(f"{path.relative_to(ROOT)}: possible secret material found")
    return problems


def validate(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    required = [
        ARTIFACT_DIR / "package.json",
        ARTIFACT_DIR / "native-proof-manifest.json",
        ARTIFACT_DIR / "src-tauri" / "Cargo.toml",
        ARTIFACT_DIR / "src-tauri" / "tauri.conf.json",
        ARTIFACT_DIR / "src-tauri" / "src" / "lib.rs",
        ARTIFACT_DIR / "src-tauri" / "src" / "main.rs",
        ARTIFACT_DIR / "src-tauri" / "capabilities" / "default.json",
        ARTIFACT_DIR / "src-tauri" / "resources" / "runner-pairing.schema.json",
    ]
    for path in required:
        if not path.exists():
            problems.append(f"missing artifact: {path.relative_to(root)}")
    if problems:
        return problems

    problems.extend(validate_manifest(load_json(ARTIFACT_DIR / "native-proof-manifest.json")))
    problems.extend(validate_package(load_json(ARTIFACT_DIR / "package.json")))
    problems.extend(validate_tauri_conf(load_json(ARTIFACT_DIR / "src-tauri" / "tauri.conf.json")))
    problems.extend(
        validate_rust_sources(
            read(ARTIFACT_DIR / "src-tauri" / "Cargo.toml"),
            read(ARTIFACT_DIR / "src-tauri" / "src" / "lib.rs"),
            load_json(ARTIFACT_DIR / "src-tauri" / "capabilities" / "default.json"),
        )
    )
    problems.extend(validate_no_secrets())
    return problems


if __name__ == "__main__":
    found = validate()
    if found:
        for problem in found:
            print(problem)
        sys.exit(1)
    print("desktop native proof artifacts: passed")
