# Agent Skills

自用 Agent 技能集合，适用于 Claude Code、Codex 等支持自定义技能的 AI 编程助手。

## 技能列表

| 技能 | 说明 |
| --- | --- |
| [caveman](caveman/SKILL.md) | 极简沟通模式，去除废话和客套，token 用量降低约 75%，同时保持技术准确性 |
| [cocos-vertical-ui-layout](cocos-vertical-ui-layout/SKILL.md) | Cocos Creator 竖屏手游 UI 布局与重构，涵盖安全文字区域、弹窗层级、多分辨率适配 |
| [diagnose](diagnose/SKILL.md) | 严格六阶段 Bug 诊断流程：复现 → 最小化 → 假设 → 插桩 → 修复 → 回归测试 |
| [game-ui-asset-sheet](game-ui-asset-sheet/SKILL.md) | 根据参考设计生成可切片的 2D 游戏 UI 素材图集，输出无文字、支持九宫格拉伸 |
| [github-gh-address-comments](github-gh-address-comments/SKILL.md) | 处理 GitHub PR Review 意见，检查未解决的讨论和内联评论，按需实施修改 |
| [github-gh-fix-ci](github-gh-fix-ci/SKILL.md) | 排查并修复 GitHub Actions 失败的 CI 检查，先分析根因再提方案 |
| [github-github](github-github/SKILL.md) | GitHub 工作流入口，自动分流到 PR Review、CI 修复、Issue 分拣等子流程 |
| [grill-me](grill-me/SKILL.md) | 连续追问式需求/方案访谈，逐层深入决策树直到达成共识 |
| [grill-with-docs](grill-with-docs/SKILL.md) | 在 grill-me 基础上，边讨论边更新项目文档（CONTEXT.md、ADR 等） |
| [handoff](handoff/SKILL.md) | 将当前对话压缩为交接文档，方便其他 Agent 或下次会话继续工作 |
| [improve-codebase-architecture](improve-codebase-architecture/SKILL.md) | 发现代码库中的浅层模块，提出重构方案使其更深层、更可测试 |
| [pdf](pdf/SKILL.md) | PDF 读取、创建、检查、渲染与校验，适用于需要精确视觉排版的场景 |
| [prototype](prototype/SKILL.md) | 快速构建一次性原型来验证设计：终端应用走逻辑分支，UI 原型走视觉分支 |
| [tdd](tdd/SKILL.md) | 测试驱动开发的红-绿-重构循环，通过公共接口验证行为而非实现细节 |
| [to-issues](to-issues/SKILL.md) | 将计划/PRD 拆解为可独立领取的 Issue，采用 tracer-bullet 纵切策略 |
| [triage](triage/SKILL.md) | Issue 分拣状态机，管理从创建到解决的完整工作流 |
| [zoom-out](zoom-out/SKILL.md) | 从更高视角审视代码段，返回相关模块和调用方的全景地图 |

## 使用方式

将技能目录复制到你的 Agent 技能路径下即可使用。具体路径取决于你使用的 Agent 工具：

- **Claude Code**: `~/.claude/skills/`
- **Codex**: `~/.codex/skills/`

部分技能依赖特定插件或工具（如 GitHub CLI、Python PDF 工具链），使用前请参阅对应 `SKILL.md` 中的前置要求。
