#!/usr/bin/env python3
"""构建实际 Magisk ZIP；本地不占号，正式输入只消费已冻结的 Core。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("JSON 不允许重复键")
        value[key] = item
    return value


def properties(data):
    pairs = [line.split("=", 1) for line in data.decode().splitlines()
             if line.strip() and not line.startswith("#")]
    if any(len(pair) != 2 for pair in pairs) or len({pair[0] for pair in pairs}) != len(pairs):
        raise ValueError("module.prop 含非法或重复字段")
    return dict(pairs)


def resolve(root, module_id):
    formal = bool(os.environ.get("FAST_DEPLOY_RUN_ID") or
                  os.environ.get("FAST_DEPLOY_CLIENT_VERSION_SNAPSHOT_FILE"))
    if formal:
        core = os.environ.get("FAST_DEPLOY_PACKAGE_CORE_ROOT")
        if not core or not Path(core).is_absolute():
            raise ValueError("正式模块需要显式冻结的 FAST_DEPLOY_PACKAGE_CORE_ROOT")
        command = [sys.executable, str(Path(core) / "shared/package_identity.py"),
                   "resolve", "--project-root", str(root), "--platform", "module",
                   "--application-id", module_id, "--architecture", "any", "--variant", "release"]
        value = json.loads(subprocess.check_output(command))
        if value["local_validation"] is not False or not 1 <= value["build_number"] <= 2147483647:
            raise ValueError("正式模块构建号必须在 Magisk versionCode 的 Int 容量内")
        return value, command
    release = root / "release.json"
    if release.is_symlink() or not release.is_file():
        raise ValueError("release.json 必须是普通文件")
    declaration = json.loads(release.read_text(), object_pairs_hook=unique_object)
    if (type(declaration) is not dict or set(declaration) != {"version"}
            or type(declaration["version"]) is not str or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)",
                                                        declaration["version"], re.ASCII)):
        raise ValueError("release.json 必须声明严格三段版本")
    return {"version": declaration["version"], "platform": "module", "application_id": module_id,
            "architecture": "any", "local_validation": True, "run_id": ""}, None


def verify(path, value, expected_files):
    with zipfile.ZipFile(path) as package:
        if sorted(package.namelist()) != sorted(expected_files):
            raise ValueError("最终 ZIP 文件集合不一致")
        for name, data in expected_files.items():
            if package.read(name) != data:
                raise ValueError("最终 ZIP 文件字节与本次输入不同")
        if package.read("build.json") != encoded(value):
            raise ValueError("最终 ZIP 身份不一致")
        props = properties(package.read("module.prop"))
        if (props["id"] != value["application_id"] or props["version"] != value["version"]
                or props["versionCode"] != str(value.get("build_number", 0))):
            raise ValueError("最终 ZIP 原生版本或构建号不一致")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"schema_version": 1, "build": value, "artifact_sha256": digest,
            "artifact_bytes": path.stat().st_size}


def build(root, artifact=None):
    if artifact is not None:
        artifact = Path(artifact)
        if (not artifact.is_absolute() or artifact.suffix != ".zip"
                or artifact.parent.resolve() != artifact.parent or not artifact.parent.is_dir()
                or artifact.is_symlink()):
            raise ValueError("正式 run 的输出必须是已有目录下的绝对 ZIP 路径，且不得经过符号链接")
        if not os.environ.get("FAST_DEPLOY_RUN_ID") or not os.environ.get("FAST_DEPLOY_CLIENT_VERSION_SNAPSHOT_FILE"):
            raise ValueError("独立 run 输出只接受完整正式输入")
    source = root / "module"
    if source.is_symlink() or (source / "module.prop").is_symlink():
        raise ValueError("模块输入不得通过符号链接读取")
    props = properties((source / "module.prop").read_bytes())
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9._-]+", props["id"], re.ASCII):
        raise ValueError("模块 ID 非法")
    if props["version"] != "@VERSION@" or props["versionCode"] != "@BUILD_NUMBER@":
        raise ValueError("module.prop 必须由构建输入生成，不能保留平行版本或编号")
    value, core_command = resolve(root, props["id"])
    files = {}
    modes = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError("模块输入只能包含普通文件和目录")
        if path.is_file():
            name = path.relative_to(source).as_posix()
            files[name] = path.read_bytes()
            modes[name] = stat.S_IMODE(path.stat().st_mode)
    if "build.json" in files:
        raise ValueError("源码不得携带旧构建身份")
    props.update(version=value["version"], versionCode=str(value.get("build_number", 0)))
    files["module.prop"] = "".join(f"{key}={item}\n" for key, item in props.items()).encode()
    files["build.json"] = encoded(value)
    modes["build.json"] = 0o644
    output = root / "dist"
    if output.is_symlink():
        raise ValueError("dist 不得是符号链接")
    output.mkdir(exist_ok=True)
    label = "local" if value["local_validation"] else "build" + str(value["build_number"])
    final = output / f"{props['id']}-{value['version']}-{label}.zip"
    with tempfile.TemporaryDirectory(prefix=".package-", dir=output) as temporary:
        candidate = Path(temporary) / "module.zip"
        with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in sorted(files.items()):
                item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | modes[name]) << 16
                item.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(item, data)
        if resolve(root, props["id"])[0] != value:
            raise ValueError("构建期间版本输入已经改变")
        report = verify(candidate, value, files)
        if core_command:
            command = core_command.copy()
            command[2] = "verify-zip"
            actual = json.loads(subprocess.check_output([*command, "--artifact", str(candidate), "--magisk"]))
            if actual != report:
                raise ValueError("Core 最终 ZIP 回读结果不同")
        if final.is_symlink():
            raise ValueError("目标安装包不得是符号链接")
        receipt = final.with_suffix(".json")
        if receipt.is_symlink():
            raise ValueError("构建收据不得是符号链接")
        if not value["local_validation"]:
            try:
                os.link(candidate, final)
            except FileExistsError:
                if final.is_symlink() or final.read_bytes() != candidate.read_bytes():
                    raise ValueError("同版本构建号已存在不同制品，拒绝覆盖")
        else:
            candidate.replace(final)
        if not value["local_validation"] and receipt.exists():
            if receipt.read_bytes() != encoded(report):
                raise ValueError("已有正式构建收据不同，拒绝覆盖")
        else:
            receipt.write_bytes(encoded(report))
    if artifact is not None:
        if value["local_validation"]:
            raise ValueError("独立 run 不接受本地验证包")
        # dist 保留原始分发包；run 路径只发布同一字节，不再生成第二种包。
        with tempfile.TemporaryDirectory(prefix=".module-run-", dir=artifact.parent) as temporary:
            candidate = Path(temporary) / "module.zip"
            shutil.copyfile(final, candidate)
            if verify(candidate, value, files) != report:
                raise ValueError("独立 run 包复制后回读不同")
            try:
                os.link(candidate, artifact)
            except FileExistsError:
                if artifact.is_symlink() or artifact.read_bytes() != candidate.read_bytes():
                    raise ValueError("独立 run 路径已有不同制品，拒绝覆盖")
        final = artifact
    return final, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path,
                        help="Core package_run.py 提供的本 run 最终 ZIP 路径")
    args = parser.parse_args()
    try:
        artifact, report = build(ROOT, args.artifact)
        value = report["build"]
        print("magisk build\n  version    " + value["version"] +
              "\n  build      " + str(value.get("build_number", "local")) +
              "\n  artifact   " + str(artifact) + "\n  sha256     " + report["artifact_sha256"])
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit("magisk build failed\n  reason     " + str(error)) from error
