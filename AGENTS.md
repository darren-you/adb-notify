# AGENTS

## 项目协作约定

- 本仓由一名维护者与 AI 长期维护。以当前需求和真实实现为依据，选择一人能够理解、执行、验证和排障的最小充分方案；不为假想团队或规模新增角色、服务和流程。
- 使用中文回复、编写文档与提交摘要。开始前读本仓 README.md 和目标子工程 README.md；项目规则源在本仓 .agents/ 中，由本文件按适用范围装配。
- 用户当前明确要求优先；更近作用域规则和真实代码、配置优先于上层说明。规则与实现冲突时先核实事实，再同步唯一规则源；不通过新增旧路径回退或重复事实源掩盖问题。
- 不确定技术事实先自行检查源码、配置和测试。确需维护者决定且问题有清晰可选项时，优先使用当前可用且允许的选择交互工具，简述选项影响；允许自由补充。默认选中、等待超时或无答复均不视为确认，已确认范围不重复询问。
- 常规开发、构建和测试使用本仓入口、锁文件及显式依赖配置，不依赖相邻 checkout 或工作区根目录。需要 SDK、外部服务或凭据时在 README 中说明准备方式；不得伪造通过结果。
- 项目设计、操作和问题正文分别保存在 docs/design、docs/operations、docs/issues，接口契约保存在 api/。仅排障时优先检索本仓 docs/issues；跨项目标准、统一发布和聚合检查由 darren-space/harness 提供，不复制成项目内的第二份工作区标准。
- 修改节点职责、入口和依赖时，同步对应 README 的架构拓扑和相关项目说明。第一方普通文档文件名使用 kebab-case；不可改写历史记录保留原事实，活动文档不因创建时间豁免。
- 修改前检查工作树、暂存区和本 Git 根 commit-message.txt，保留已有改动。实际文件修改后追加不重复的中文 `- 变更摘要`；不在普通子目录新增记录。记录只描述未提交变更。
- 在 darren-space 中提交、推送和依赖同步使用工作区 Git 入口及共享记录锁；独立 checkout 的开发和测试不以该入口可用为前提。第一方默认分支保持 master；逻辑仓名、GitHub 仓名与 checkout basename 使用同一 kebab-case 身份，所属路径由 resolver 读取。部署单元、语言模块和平台安装身份按各自命名空间显式映射，不要求与仓名同一个字符串。
- 统一发布仍通过 darren-space 的 Fast Deploy。需要发布时读取实际 deploy_config.sh 与已登记 Job；本地测试和 Git 保存分别报告，不能等同于线上发布通过。
- 敏感配置只消费明确授权的既有事实源，不回显值，不因时间、私有会话读取或一般建议自行更换凭据。
- 涉及数据库、持久化、迁移或字段映射时，先修改真实 Schema、迁移、源码及全部实际消费者，再同步文档。聚合检查和发布遵循 `harness/docs/workspace/standards/database/database_golden_path.md`，项目本地验证按本仓说明执行。

## 命名规范与硬切边界

- 本节是现有与新增第一方名称的统一目标规则，按实际消费者选用；未采用的技术不要求新增工程或运行面。当前源码、路径与协议值用于定位实施对象，不因已存在、被称为装配边界或写入项目规则而豁免。规则落盘不等于源码、数据或生产迁移完成；无关任务不顺带启动全量改名。
- 先识别语义和命名空间，再确定拼写、检查碰撞并闭合引用。展示名、仓库 ID、语言包、发布单元、平台安装身份分别声明；跨层显式映射，不用全局大小写转换器处理任意 JSON、路径或 ID。完整裁决与官方依据见工作区 `harness/docs/design/darren-space/global/naming-conventions-hard-cutover-plan.md`；尚未采用的语言、框架与基础设施接入前核对其中对应规则，不另选风格。
- 同一概念使用同一术语；实体用单数，集合用复数，操作用动词，布尔值表达肯定判断。无类型保障的数值写明单位，如 `timeout_ms`、`size_bytes`、`amount_minor` 配 `currency`；时刻、日期和时长不能混用。缩写遵从语言：Go／Swift 的 `userID`、TS／Java／Dart 的 `userId`、Python／wire 的 `user_id`。

### 仓库、文件与语言

- 仓库、产品 slug、工作区逻辑 ID、普通职责目录、普通文档／配置 basename 和自有静态资源使用 kebab-case；仓库 basename 与逻辑 ID 一致，所属路径只从 resolver 读取。语言包目录按语言规则；生成文件从生成器／Schema／模板修改。第一方默认分支只用 `master`，普通主题分支 kebab-case，可带用途前缀；正式版本 tag 用 `v<major>.<minor>.<patch>`，子目录语言模块发布按包管理器 tag 规则。
- 平台固定入口、构建选择后缀、标准字段、接口回调、原样第三方源码和外部不透明 ID 按所属系统精确保留，例如 `README.md`、`AGENTS.md`、`Package.swift`、`_test.go`、`.d.ts`、`.g.dart`；自创入口不能仅因有读取器就豁免。不可改写的审计／迁移历史保留原事实，仍在消费的第一方活动文档不能因创建时间豁免。
- 第一方跨平台路径禁止空格、控制字符、尾随空格／点、Windows 禁止字符及保留设备名；同级名称不得仅大小写不同。改名检查大小写折叠、Unicode 规范化、生成与截断碰撞；纯大小写改名用临时中间路径，验证 Git 索引及大小写敏感构建，不能靠 `core.ignoreCase` 或未跟踪旧文件掩盖问题。
- Go：源码 snake_case，普通 package 简短全小写且无下划线／连字符；导出 PascalCase，非导出 lowerCamelCase，缩写如 `HTTPClient`、`requestID`。外部测试包 `<name>_test`、`internal/vendor/testdata`、测试及 OS／arch 后缀保留工具语义；module import path 与 package 名分开。
- Python／MicroPython：文件、包、函数和变量 snake_case，类型 PascalCase，常量 UPPER_SNAKE_CASE；启动／协议入口原样。distribution 用 kebab-case，import 用 snake_case，wheel 由工具按规范生成，不新增同义包或私造双下划线协议名。
- TS／JS：所有普通源码文件与目录用 kebab-case，组件文件也如此；类型／组件符号 PascalCase，函数／变量 lowerCamelCase，真实 Hook 使用 `useXxx`；语义常量／enum 成员 UPPER_SNAKE_CASE，普通 `const` 不因此大写。框架特殊路由入口、ESM／CommonJS 后缀与第三方属性按真实合同；npm 发布包用受控 scope 与 kebab-case 包名。
- Swift：类型文件、package 声明、target、module 用真实产品／职责的 PascalCase，扩展文件 `Type+Capability.swift`；成员、常量、enum case 为 lowerCamelCase，缩写按 Swift 规则。SwiftPM dependency identity、产品／二进制名、Bundle ID 与展示名分别声明，不能从包展示名或仓库 slug 机械推导。
- Kotlin／Java：package 全小写，主类型文件与 PascalCase 类型同名，方法／变量 lowerCamelCase，真正常量与 enum 成员 UPPER_SNAKE_CASE；生命周期和重写签名原样。Jetpack Compose 的 `@Composable` 返回 `Unit` 时用 PascalCase 名词，非 `Unit` 使用 lowerCamelCase；内部 `remember` 并返回可变对象的工厂用 `rememberXxx`。Dart：包、目录、文件 snake_case，类型 PascalCase，成员、const 与 enum value lowerCamelCase，保留库私有和生成后缀语义。
- C／ESP-IDF：文件、组件、函数及变量 snake_case，跨组件符号带组件前缀，typedef 使用 `<component>_<noun>_t`，宏／枚举值 UPPER_SNAKE_CASE。第一方通用 C++：文件／namespace／变量 snake_case，类型和普通函数 PascalCase，真正常量及枚举值 `kPascalCase`，class 数据成员尾随 `_`；内核、STL、JNI、SDK ABI 和生成入口按其精确合同。
- Shell：内部脚本／库、函数与局部变量 snake_case，人工 CLI／子命令／长选项 kebab-case，环境变量／常量 UPPER_SNAKE_CASE；不覆盖系统变量，不为旧名保留 wrapper，按 shebang 区分 Bash、sh 和 ash。PowerShell 使用 Approved `Verb-Noun` 与单数名词；Ruby 文件／方法 snake_case、类型 PascalCase、常量 UPPER_SNAKE_CASE，`?`／`!` 按真实方法语义。

### 数据、协议与资源

- 自有 SQL database/schema/table/column、Mongo database/collection/BSON 字段使用 snake_case，可数实体表／集合用复数；引擎固定名、GridFS 字段及实际长度／折叠限制按平台。Schema、正式迁移、ORM／查询、DTO 与客户端映射共同修改，不编辑已执行迁移伪造历史；保留数据、归属、约束和权限，不因改名建立数据库备份／恢复链。
- Redis 只承载可重建缓存；缓存 key 按 `<owner>[:<env>]:<resource>:v<schema_version>:<id>[:<purpose>]` 分层，静态段 snake_case；动态 ID 保持业务语义并编码成合法单段，不得注入分隔符或 hash tag。锁、幂等与去重 key 按真实业务并发作用域验证，不机械套用缓存版本；更名时必须先闭合真实并发语义，不能让新旧 key 形成两把可同时获得的锁。本地设置与普通运行时翻译字典 key 用点分 snake_case；持久化 key 改名必须迁移实际数据，不能用清空设置冒充完成。
- 普通 REST、query／multipart、自有 WebSocket／插件消息及 MCP 输入输出的自有字段使用 snake_case，业务 wire enum 用 snake_case；引用产品／渠道等身份的值服从其所属命名空间。语言模型通过显式 DTO／序列化映射消费。OpenAPI 固定关键字原样，schema 名 PascalCase、operationId lowerCamelCase、tag kebab-case；四字段响应 envelope 的既有语义保持。
- 普通请求关联目标为 HTTP `Request-Id` 与 `request_id`；真实分布式 tracing 的 `trace_id`、`span_id`、`traceparent` 保留原语义，不能直接改名冒充请求 ID。共享合同切换须覆盖入口、响应、日志与真实消费者，不能仅改客户端。GraphQL 字段 lowerCamelCase；Protobuf 字段 snake_case、ProtoJSON 输出按标准 lowerCamelCase，并保留标准解析行为；第三方 payload、签名原文及用户 map key 不自动转换。
- 普通 URL 静态段 kebab-case，集合资源复数，canonical 路径除根外无末尾 `/`；不透明路径 ID 不改大小写。locale 使用 BCP 47 canonical 拼写，如 `zh-CN`／`zh-Hant`，页面路径、消息文件、路由、hreflang 和构建输出一致；`og:locale` 只使用明确的 `language_TERRITORY` 映射，不把 script 当地区。HTTP header 按协议大小写不敏感语义验证，不为显示形式发明拒绝规则。
- 普通自有 JSON／YAML／TOML 配置键 snake_case，环境变量 UPPER_SNAKE_CASE；工具原生关键字、Helm values 的 lowerCamelCase、Terraform 逻辑符号的 snake_case 等按明确边界。CSS class、自有 data 属性、CSS 变量使用 kebab-case。Android 普通资源 snake_case、style／theme PascalCase 点分并验证继承、attr lowerCamelCase、styleable PascalCase；Flutter gen-l10n 生成 key 用合法 lowerCamelCase 标识符，不能套点分字典规则。
- MCP 工具名固定 `<domain>.<resource>.<verb>` 三段，段内 snake_case；自有消息类型用点分 snake_case 域与动作／事件。MQTT topic 用 `/` 分层、静态段 kebab-case，设备 ID 原样；迁移同时覆盖真实固件、发布订阅、ACL、retained／session。ESP NVS key／namespace 使用 snake_case 且最多 15 个 ASCII 字符，partition label 最多 15 个有效字节；设备身份算法、Kconfig、Soong、SELinux、Magisk 和 ABI 固定入口不能机械改写。

### 发布身份与实施验收

- 部署单元统一 `<repo-id>-<role>`，同一单元的 Job name 与 `PROJECT_NAME` 精确相等，产生制品时 `artifact_contract.project_name` 也必须一致；物理目录由显式配置定位，移动目录不暗中更换发布身份。部署设备目标用 `deploy_target`／`DEPLOY_TARGET`，多目标 `deploy_targets`；`build_host` 表达构建宿主，`region` 只表达真实地域。设备身份从既有 inventory／resolver 读取，不另建别名表。
- 没有部署设备维度的 Job／制品不填 `deploy_target`；不得塞入 `global` 或构建宿主，也不为无行为差异新增范围字段。旧维度切换必须覆盖 UI、API、JobManifest、队列／持久化记录、调度、脚本、制品构造／解析／匹配与真实发布；缺省目标不能成为匹配任意设备的通配符。
- Compose 自有 service／network／volume key 和容器／服务自有名 kebab-case；模型 key、实际资源名、挂载与生命周期分别验证，已合规实际名不因 key 改名搬迁。显式 `name` 不保证指向已有数据，不得误建空卷。systemd 使用 `<service-id>.service`，launchd Label 使用 `com.xdarren.<product>.<role>`；Apple／Android 安装身份按受控反域名及平台注册合同，不能把改名变成新安装身份或权限对象。
- 一个硬切批次由完整消费者集合决定；声明、生成器、源码、测试、配置、存储与运行面一次收敛，不保留自有旧名别名、软链接、双字段读写、双 topic 或旧路由。允许一次性离线转换读取旧格式，完成后删除迁移接线；外部平台原生重定向／标准解析不冒充自有兼容层。离线设备、已安装客户端或不可变平台 ID 未具备切换条件时，明确尚未完成，不能伪造闭环。
- 改名必须保持业务语义、数据归属、真实目标与权限，不自行更换有效凭据或扩展产品能力。受管源码模块变更按版本合同同步全部真实派生消费者；纯物理归位且模块相对文件名、内容、执行位与装配合同均不变时不升版本。Core 通过既有升级入口，按本次实际受影响的消费集合显式选择完整目标 SHA 并更新精确 gitlink，普通 Core scoped 保存不隐式升级消费者。按受影响边界验证编译／import、真实序列化与解码、数据查询与挂载、运行态与正式入口；仅规则同步、静态扫描或本地构建不能证明生产迁移完成。

## Client API Response Contract

- 普通 REST JSON 的客户端 DTO 与真实网络解码入口必须共同遵守 `code / timestamp / msg / data` 四字段合同；不能把 TypeScript 类型断言、Swift 合成解码或模板文件一致当作运行时验证。`timestamp` 与 `msg` 必需，`data:null` 不能与缺少 `data` 混同；拒绝额外顶层字段、旧 `message`、旧成功码 `0` 和裸业务 JSON 兼容路径。
- Auth 错误严格按唯一 OpenAPI 的 `data.error_code` 与已声明关联字段解析，禁止退回旧 `data.error.code/message`。请求关联的命名目标为 `request_id`／`Request-Id`，真实 tracing 才使用 `trace_id`；切换必须同时闭合 OpenAPI、Server、SDK、受管派生模块及真实解码，不能仅改客户端或新增双字段兼容。HTTP 失败和业务失败均不能被客户端当作成功返回；health 按同一 envelope 读取 `data.service`。
- 新增或修改 DTO、JSON 网络读取、错误映射时，必须运行该工程真实请求/解码回归；聚合检查与发布时另运行 `python3 harness/scripts/check_client_response_contract.py --repo <逻辑仓库名>`；回归至少覆盖成功、失败、null、缺字段、额外字段和旧格式。Web 的 DTO 回归必须进入实际 `npm run build` 链路，不能只留下不会执行的测试文件；Swift 测试必须进入实际使用的 SwiftPM / Xcode target。
- 客户端合同检查由工程标准、总治理和对应构建发布链路执行；Git push 与 dry-run 只负责保存和传输代码快照，不执行该质量检查，允许 task 在未完成时保存。发现新解析形态时扩展检查器及失败回归，不能添加产品白名单或仅靠 AGENTS 口头保证；push 成功不能替代构建、测试和发布验证。完整边界见 `harness/docs/workspace/standards/client_response_contract.md`。

## ADB Notify Scope

- 本仓库维护 USB 系统通知开关 Magisk 模块。
- 模块只处理“已连接到 USB 调试”通知和“正在通过 USB 为此设备充电”通知，不处理第三方前台服务通知。
- 生成的安装 zip 属于构建产物，默认不提交；正式可安装包通过 GitHub Release 发布。
- Magisk 模块相关行为优先参考 `harness/docs/workspace/standards/magisk_module/magisk_module_golden_path.md`，以及当前仓库 README 中的实际边界。
