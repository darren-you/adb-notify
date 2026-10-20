#!/usr/bin/env python3
"""真实 ZIP 回读；正式场景显式提供 Core 源码，并在临时 Git/状态空间运行。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_package as package


def commit(root):
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-qm", "冻结测试源码"], check=True)
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


class PackageFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "module-repo"
        self.root.mkdir()
        for name in ("module", "scripts"):
            shutil.copytree(package.ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in (".gitignore", "release.json"):
            shutil.copy2(package.ROOT / name, self.root / name)
        environment = {key: value for key, value in os.environ.items() if not key.startswith("FAST_DEPLOY_")}
        self.environment = patch.dict(os.environ, environment, clear=True)
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()


class PackageTest(PackageFixture):
    def test_invalid_local_declarations_are_rejected(self):
        release = self.root / "release.json"
        for value in ('{"version":"1.0.0","version":"1.0.1"}', '{"version":true}',
                      '{"version":"01.0.0"}', '["1.0.0"]'):
            release.write_text(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                package.build(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_local_zip_has_native_fields_and_preserves_old_artifacts(self):
        output = self.root / "dist"
        output.mkdir()
        (output / "old.zip").write_bytes(b"historical bytes")
        path, report = package.build(self.root)
        self.assertEqual((output / "old.zip").read_bytes(), b"historical bytes")
        self.assertTrue(report["build"]["local_validation"])
        self.assertNotIn("build_number", report["build"])
        with zipfile.ZipFile(path) as archive:
            props = package.properties(archive.read("module.prop"))
            self.assertEqual((props["version"], props["versionCode"]), ("1.0.0", "0"))
            self.assertEqual(archive.read("service.sh"), (self.root / "module/service.sh").read_bytes())
            self.assertEqual(archive.getinfo("system/bin/usb-adb-notify").external_attr >> 16 & 0o777,
                             (self.root / "module/system/bin/usb-adb-notify").stat().st_mode & 0o777)
        digest = report["artifact_sha256"]
        self.assertEqual(package.build(self.root)[1]["artifact_sha256"], digest)

    def test_parallel_versions_and_external_links_fail_before_packaging(self):
        path = self.root / "module/module.prop"
        original = path.read_text()
        path.write_text(original.replace("@BUILD_NUMBER@", "3"))
        with self.assertRaisesRegex(ValueError, "平行版本"):
            package.build(self.root)
        path.write_text(original)
        (self.root / "module/outside").symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, "普通文件"):
            package.build(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_incomplete_formal_environment_cannot_fall_back_to_local(self):
        os.environ["FAST_DEPLOY_RUN_ID"] = "missing"
        with self.assertRaisesRegex(ValueError, "冻结的"):
            package.build(self.root)
        self.assertFalse((self.root / "dist").exists())


@unittest.skipUnless(os.environ.get("FAST_DEPLOY_TEST_PACKAGE_CORE_ROOT"), "正式输入测试需要显式 Core 测试源码")
class FormalPackageTest(PackageFixture):
    def setUp(self):
        core_source = Path(os.environ["FAST_DEPLOY_TEST_PACKAGE_CORE_ROOT"])
        super().setUp()
        self.core = self.base / "core"
        shutil.copytree(core_source / "shared", self.core / "shared",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for root in (self.root, self.core):
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            commit(root)
        self.core_sha = subprocess.check_output(["git", "-C", str(self.core), "rev-parse", "HEAD"], text=True).strip()
        self.state_root = self.base / "artifacts"
        self.state_root.mkdir(mode=0o700)
        sys.path.insert(0, str(self.core / "shared"))
        import release_version_state
        import client_version
        self.state = release_version_state
        self.version = client_version
        os.environ["FAST_DEPLOY_PACKAGE_CORE_ROOT"] = str(self.core)

    def allocate(self, run, version="1.0.0", floor=3):
        declaration = self.root / "release.json"
        if json.loads(declaration.read_text())["version"] != version:
            declaration.write_text(json.dumps({"version": version}) + "\n")
            commit(self.root)
        sha = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "-C", str(self.root), "update-ref", "refs/remotes/origin/" + version, sha], check=True)
        context = dict(source_ref="refs/heads/" + version, run_id=run, repo_name="adb-notify",
                       resolved_commit_sha=sha, core_commit_sha=self.core_sha, job_manifest_sha256="b" * 64,
                       profile_snapshot_id="c" * 64, config_path="release.json", build_env="", build_type="release",
                       build_channel="", artifact_kind="module")
        os.environ.update({self.version.CONTEXT_ENV_FIELDS[key]: value for key, value in context.items()})
        scope = self.version.scope_from_context(context, "module", "usb-adb-notify-toggle")
        if not (self.state_root / "release-versions" / self.state.scope_key(scope)).exists():
            self.state.initialize(self.state_root, scope, floor, self.core_sha)
        result = self.state.allocate(self.state_root, self.root, "module", scope["application_id"],
                                     "release", ["any"], dict(os.environ), self.core)
        snapshot = self.base / "snapshot.json"
        snapshot.write_text(json.dumps({"protocol_version": 1, "ok": True,
                                        "version_snapshot": result["version_snapshot"]}))
        os.environ["FAST_DEPLOY_CLIENT_VERSION_SNAPSHOT_FILE"] = str(snapshot)

    def test_actual_zip_two_builds_replay_and_version_change(self):
        hashes = {}
        for run, version, number in (("first", "1.0.0", 4), ("first", "1.0.0", 4),
                                      ("second", "1.0.0", 5), ("next-version", "1.0.1", 6)):
            self.allocate(run, version)
            path, report = package.build(self.root)
            self.assertEqual((report["build"]["version"], report["build"]["build_number"]), (version, number))
            if run in hashes:
                self.assertEqual(hashes[run], report["artifact_sha256"])
            hashes[run] = report["artifact_sha256"]
            with zipfile.ZipFile(path) as archive:
                props = package.properties(archive.read("module.prop"))
                self.assertEqual((props["version"], props["versionCode"]), (version, str(number)))
        self.assertEqual(len(list((self.root / "dist").glob("*.zip"))), 3)

    def test_dirty_core_wrong_identity_or_source_cannot_package(self):
        self.allocate("first")
        with self.assertRaises(subprocess.CalledProcessError):
            package.resolve(self.root, "another-module")
        path = self.core / "shared/package_identity.py"
        original = path.read_bytes()
        path.write_bytes(original + b"\n# changed\n")
        with self.assertRaises(subprocess.CalledProcessError):
            package.build(self.root)
        path.write_bytes(original)
        path = self.root / "module/common.sh"
        path.write_bytes(path.read_bytes() + b"\n# changed\n")
        with self.assertRaises(subprocess.CalledProcessError):
            package.build(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_native_overflow_and_replacing_existing_formal_bytes_are_rejected(self):
        self.allocate("first")
        path, _ = package.build(self.root)
        path.write_bytes(b"existing different artifact")
        with self.assertRaisesRegex(ValueError, "不同制品"):
            package.build(self.root)
        self.assertEqual(path.read_bytes(), b"existing different artifact")
        # 不修改既有计数器，使用另一独立临时状态验证原生容量。
        self.state_root = self.base / "capacity-state"
        self.state_root.mkdir(mode=0o700)
        self.allocate("overflow", floor=2147483647)
        with self.assertRaisesRegex(ValueError, "Int 容量"):
            package.build(self.root)
        self.assertEqual(len(list((self.root / "dist").glob("*.zip"))), 1)


if __name__ == "__main__":
    unittest.main()
