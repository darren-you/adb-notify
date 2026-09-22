# AGENTS

## 项目协作约定

- 本仓由一名维护者与 AI 长期维护。以当前需求和真实实现为依据，选择一人能够理解、执行、验证和排障的最小充分方案；不为假想团队或规模新增角色、服务和流程。
- 使用中文回复、编写文档与提交摘要。开始前读本仓 README.md 和目标子工程 README.md；项目规则源在本仓 .agents/ 中，由本文件按适用范围装配。
- 用户当前明确要求优先；更近作用域规则和真实代码、配置优先于上层说明。规则与实现冲突时先核实事实，再同步唯一规则源；不通过新增旧路径回退或重复事实源掩盖问题。
- 不确定技术事实先自行检查源码、配置和测试。确需维护者决定且问题有清晰可选项时，优先使用当前可用且允许的选择交互工具，简述选项影响；允许自由补充。默认选中、等待超时或无答复均不视为确认，已确认范围不重复询问。
- 常规开发、构建和测试使用本仓入口、锁文件及显式依赖配置，不依赖相邻 checkout 或工作区根目录。需要 SDK、外部服务或凭据时在 README 中说明准备方式；不得伪造通过结果。
- 项目设计、操作和问题正文分别保存在 docs/design、docs/operations、docs/issues，接口契约保存在 api/。仅排障时优先检索本仓 docs/issues；跨项目标准、统一发布和聚合检查由 darren-space/harness 提供，不复制成项目内的第二份工作区标准。
- 修改节点职责、入口和依赖时，同步对应 README 的架构拓扑和相关项目说明。普通文档文件名使用 kebab-case；历史材料按真实叙述保留。
- 修改前检查工作树、暂存区和本 Git 根 commit-message.txt，保留已有改动。实际文件修改后追加不重复的中文 `- 变更摘要`；不在普通子目录新增记录。记录只描述未提交变更。
- 在 darren-space 中提交、推送和依赖同步使用工作区 Git 入口及共享记录锁；独立 checkout 的开发和测试不以该入口可用为前提。默认分支保持 master；逻辑仓名、GitHub 仓名、物理归属路径与部署身份使用同一个 kebab-case 身份。
- 统一发布仍通过 darren-space 的 Fast Deploy。需要发布时读取实际 deploy_config.sh 与已登记 Job；本地测试和 Git 保存分别报告，不能等同于线上发布通过。
- 敏感配置只消费明确授权的既有事实源，不回显值，不因时间、私有会话读取或一般建议自行更换凭据。
- 涉及数据库、持久化、迁移或字段映射时，先修改真实 Schema、迁移、源码及全部实际消费者，再同步文档。聚合检查和发布遵循 `harness/docs/workspace/standards/database/database_golden_path.md`，项目本地验证按本仓说明执行。

## Client API Response Contract

- 普通 REST JSON 的客户端 DTO 与真实网络解码入口必须共同遵守 `code / timestamp / msg / data` 四字段合同；不能把 TypeScript 类型断言、Swift 合成解码或模板文件一致当作运行时验证。`timestamp` 与 `msg` 必需，`data:null` 不能与缺少 `data` 混同；拒绝额外顶层字段、旧 `message`、旧成功码 `0` 和裸业务 JSON 兼容路径。
- Auth 错误按 OpenAPI 的 `data.error_code / trace_id` 解析，禁止退回旧 `data.error.code/message`。HTTP 失败和业务失败均不能被客户端当作成功返回；health 按同一 envelope 读取 `data.service`。
- 新增或修改 DTO、JSON 网络读取、错误映射时，必须运行该工程真实请求/解码回归；聚合检查与发布时另运行 `python3 harness/scripts/check_client_response_contract.py --repo <逻辑仓库名>`；回归至少覆盖成功、失败、null、缺字段、额外字段和旧格式。Web 的 DTO 回归必须进入实际 `npm run build` 链路，不能只留下不会执行的测试文件；Swift 测试必须进入实际使用的 SwiftPM / Xcode target。
- 客户端合同检查由工程标准、总治理和对应构建发布链路执行；Git push 与 dry-run 只负责保存和传输代码快照，不执行该质量检查，允许 task 在未完成时保存。发现新解析形态时扩展检查器及失败回归，不能添加产品白名单或仅靠 AGENTS 口头保证；push 成功不能替代构建、测试和发布验证。完整边界见 `harness/docs/workspace/standards/client_response_contract.md`。

## ADB Notify Scope

- 本仓库维护 USB 系统通知开关 Magisk 模块。
- 模块只处理“已连接到 USB 调试”通知和“正在通过 USB 为此设备充电”通知，不处理第三方前台服务通知。
- 生成的安装 zip 属于构建产物，默认不提交；正式可安装包通过 GitHub Release 发布。
- Magisk 模块相关行为优先参考 `harness/docs/workspace/standards/magisk_module/magisk_module_golden_path.md`，以及当前仓库 README 中的实际边界。
