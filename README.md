# USB Notify Magisk 模块

这个 Magisk 模块用于切换 Android 的 USB 调试常驻通知和 USB 充电/连接通知。

默认行为：隐藏“已连接到 USB 调试”通知和“正在通过 USB 为此设备充电”通知。

## 架构拓扑

```mermaid
flowchart TB
    source["module/ · Magisk 模块源码"]
    build["scripts/build.sh · 构建入口"]
    zip["dist/ 与 GitHub Release · 安装 ZIP"]
    magisk["Android Magisk"]
    early["post-fs-data.sh · 开机早期属性设置"]
    late["service.sh 与 action.sh · 晚启动和手动切换"]
    property["persist.adb.notify · ADB 通知开关"]
    notifications["Android Notification Service · USB 系统通知"]
    cli["system/bin/usb-adb-notify · 状态与切换 CLI"]

    source -->|"打包"| build
    build -->|"生成可安装产物"| zip
    zip -->|"安装模块"| magisk
    magisk -->|"开机执行"| early
    magisk -->|"晚启动或点击 Action 执行"| late
    early -->|"写入系统属性"| property
    late -->|"隐藏或恢复当前通知"| notifications
    cli -->|"触发 on、off 或 toggle"| late
    property -->|"控制 USB 调试通知"| notifications
```

## 原理

ADB 调试通知由 AOSP `UsbDeviceManager.updateAdbNotification()` 读取 `persist.adb.notify` 控制：

- `persist.adb.notify=0`：不显示 USB 调试通知。
- `persist.adb.notify=1`：恢复 Android 默认显示行为。

USB 充电/连接通知没有对应的 `persist.adb.notify` 属性开关，模块通过 `cmd notification snooze` 隐藏当前 Android 系统 USB 通知。

模块在开机早期通过 `post-fs-data.sh` 写入 ADB 属性，在 late start 阶段通过 `service.sh` 补做当前通知隐藏。当前处理的通知 key：

- USB 调试通知：`-1|android|26|null|1000`
- USB 充电/连接通知：`-1|android|32|null|1000`

## 安装

下载 release 中的 `usb-adb-notify-toggle-v1.0.2.zip`，在 Magisk 中安装，然后重启。

也可以本地构建：

```sh
./scripts/build.sh
```

构建产物会生成在 `dist/`。

## 使用

可以在 Magisk 模块列表里点击本模块的 Action 按钮切换，也可以执行：

```sh
su -c usb-adb-notify status
su -c usb-adb-notify off
su -c usb-adb-notify on
su -c usb-adb-notify toggle
```

`off` 会设置 `persist.adb.notify=0`，并隐藏 USB 调试通知与 USB 充电/连接通知。

`on` 会设置 `persist.adb.notify=1`，并恢复系统默认显示行为。

## 注意

- 本模块只处理 USB 调试通知和 USB 充电/连接通知，不处理 FIClash、VPN、投屏、文件传输工具等第三方前台服务通知。
- `post-fs-data.sh` 会在开机早期写入属性，`service.sh` 会在晚启动阶段补做当前通知隐藏。
- 从隐藏切回显示时，通知不一定立刻重新出现；通常需要重插 USB、切换 USB 调试或重启后触发系统重新发通知。
- 卸载模块时会恢复 `persist.adb.notify=1`，并 unsnooze 当前模块处理的系统通知，避免把设备长期留在隐藏状态。

## 目录结构

```text
module/
  META-INF/com/google/android/
  action.sh
  common.sh
  customize.sh
  module.prop
  post-fs-data.sh
  service.sh
  system/bin/usb-adb-notify
  uninstall.sh
scripts/
  build.sh
```

## 工作区治理

本仓库纳入 `darren-space` 后按轻量 tooling repo 管理：

- 工作区标准入口：`../../harness/docs/workspace/standards/README.md`
- 终端脚本输出标准：`../../harness/docs/workspace/standards/tooling/terminal_output_golden_path.md`
- Magisk 模块标准：`../../harness/docs/workspace/standards/magisk-module/magisk_module_golden_path.md`

## 参考资料

- AOSP `UsbDeviceManager`：<https://android.googlesource.com/platform/frameworks/base/+/5ac72a2/services/java/com/android/server/usb/UsbDeviceManager.java>
- Magisk Developer Guides：<https://magisk.readthedocs.io/en/latest/developers/guides.html>

## License

GPL-3.0。模块安装器脚本来自 Magisk 官方模块 installer 机制，按 GPL 授权发布更稳妥。
