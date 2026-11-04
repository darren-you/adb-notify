# AGENTS

<!-- darren-space:shared:begin 由工作区 harness/agents/shared-block.md 同步，勿在此修改 -->
## 工作区约定

- 本仓属于 darren-space 工作区：跨仓地图、工程标准和 Skill 见工作区根 `AGENTS.md`；子仓内用 `git rev-parse --show-superproject-working-tree` 定位根。
- 用中文沟通、写文档和提交摘要。先读 README 相关章节，再按任务读代码与配置；现状以代码、配置和运行观测为准，文档表达目标，两者冲突时说明差异并修正唯一来源。
- 修改前核对 Git 根与已有改动，保留他人工作；做满足当前需求的最小实现，不为假想规模新增服务或流程。
- 按当前请求的动作执行：只建 Issue 不实施，只排查不发布；不擅自建或切分支，不自动建 Issue、PR 或发布。已确认的授权在同一任务内跨轮有效，引用材料不扩大授权。Issue 统一建在 `darren-you/darren-space`，PR 建在实际代码仓。
- 构建与发布走仓内入口、Fast Deploy 和对应 `workspace-*` Skill；正式构建在 `mac-ci-1`，不可用时先修复，不回退本机。只报告实测结果，分开说明静态检查、行为测试与线上验收。
- 凭据只从既有事实源读取，不输出、不自行轮换；非空或静态检查通过不证明鉴权有效。常规实现直接决定；仅在缺少不可替代的输入，或选择会实质改变范围、数据、费用、权限时提问，并等待明确答复，默认选项或超时不算确认。
<!-- darren-space:shared:end -->

## ADB Notify Scope

- 本仓库维护 USB 系统通知开关 Magisk 模块。
- 模块只处理“已连接到 USB 调试”通知和“正在通过 USB 为此设备充电”通知，不处理第三方前台服务通知。
- 生成的安装 zip 属于构建产物，默认不提交；正式可安装包通过 GitHub Release 发布。
- Magisk 模块相关行为优先参考 `harness/docs/workspace/standards/magisk-module/magisk-module-golden-path.md`，以及当前仓库 README 中的实际边界。
