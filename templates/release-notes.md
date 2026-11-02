# <技能名称> v<版本号>

> 这是 GitHub Release 的发布说明。填完直接粘进 Release 编辑框。
> 删掉所有尖括号占位内容；不需要的段落整段删掉。

## 一句话

<一句话说清这个技能解决什么问题、输入什么、输出什么。>

## 装上就能用

```bash
# 从 Release 下载（推荐）
unzip <repo>-v<版本号>.zip -d ~/.workbuddy/skills/

# 或从源码克隆
git clone https://github.com/<owner>/<repo>.git ~/.workbuddy/skills/<skill-name>
```

## 怎么用

在对话里这样说就会触发：

| 你会这样说 | 会发生什么 |
|---|---|
| 「<示例 1>」 | <结果> |
| 「<示例 2>」 | <结果> |

## 需要准备什么

- <依赖 1>（例：需要 ffmpeg → `brew install ffmpeg`）
- <凭证 1>（例：需要某 API Key → 填在 `~/.xxx/config.env`，模板见仓库里的 `config.example.env`）

## 本版本变更

<列出本版本相对上一版的改动，一句话一条。完整记录见 CHANGELOG.md。>

## 边界与不做的事

- **不做**：<例：只推到草稿箱，不代替你发布>
- **需要你自己做的**：<例：最后点一下确认>

## 反馈

- 问题反馈：<Issue 链接>
- 仓库：<https://github.com/...>
- 许可证：MIT
