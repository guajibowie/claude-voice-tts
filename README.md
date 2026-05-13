# Claude Voice TTS

让 Claude Code 用语音朗读回复。基于 Microsoft Edge TTS (edge-tts)。

## 功能

- **回复语音**：Claude 回复后自动朗读口语摘要
- **权限提示**：弹出权限请求时语音播报（支持中英双语）
- **语音切换**：`/voice-config` 随时切换语音角色和语言
- **自动清理**：临时文件播完即删，不留垃圾

## 安装

### 前置条件

```bash
pip install edge-tts
```

### 方式一：插件目录

```bash
git clone https://github.com/guajibowie/claude-voice-tts.git
cd 你的项目目录
claude --plugin-dir ../claude-voice-tts
```

### 方式二：全局 skills（推荐个人使用）

```bash
git clone https://github.com/guajibowie/claude-voice-tts.git
cp -r claude-voice-tts/skills/* ~/.claude/skills/
```

### 方式三：直接复制

将 `skills/voice-setup/`、`skills/voice-config/`、`skills/voice-disable/` 复制到任意项目的 `.claude/skills/` 目录。

## 使用

在任何 Claude Code 会话中输入：

| 命令 | 作用 |
|------|------|
| `/voice-setup` | 一键配置语音输出（hooks + CLAUDE.md） |
| `/voice-config` | 查看/切换语音角色或语言 |
| `/voice-config --list zh-CN` | 列出所有中文语音 |
| `/voice-disable` | 移除语音输出配置 |

配置完成后重启 Claude Code。

## 工作原理

```
Claude 回复 → 写入口语摘要到 last_response.txt → Stop hook 触发 → edge-tts 朗读
权限弹窗 → PermissionRequest hook 触发 → edge-tts 朗读权限类型
```

## 语音角色

常用语音（更多见 `/voice-config --list`）：

| 语言 | 女声 | 男声 |
|------|------|------|
| 中文 | zh-CN-XiaoxiaoNeural | zh-CN-YunyangNeural |
| 英文(US) | en-US-JennyNeural | en-US-GuyNeural |
| 英文(UK) | en-GB-SoniaNeural | en-GB-RyanNeural |
| 日语 | ja-JP-NanamiNeural | ja-JP-KeitaNeural |

## 许可

MIT
