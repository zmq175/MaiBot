# Fish Audio TTS Plugin for MaiBot

一个为MaiBot提供高质量文本转语音功能的插件，使用Fish Audio API，支持LLM智能判断和代理访问。

## 功能特性

- 🎯 **LLM智能判断**: 在Focus模式和Normal模式下都使用LLM判断何时触发TTS
- 🌐 **代理支持**: 支持代理配置，解决部分地区无法直接访问Fish Audio的问题
- 🎵 **高质量语音**: 使用Fish Audio的先进TTS模型生成自然流畅的语音
- 🔄 **自动重试**: 内置重试机制，提高API调用的成功率
- 📝 **手动触发**: 提供命令接口，支持手动触发TTS功能
- ⚙️ **灵活配置**: 支持详细的配置选项，包括语音参数、代理设置等

## 安装配置

### 1. 环境变量配置

在MaiBot根目录的`.env`文件中添加以下配置：

```env
# Fish Audio API配置
FISH_AUDIO_API_KEY=your_api_key_here
FISH_AUDIO_MODEL_ID=your_model_id_here

# 代理配置（可选，如果无法直接访问Fish Audio）
FISH_AUDIO_PROXY_URL=http://your_proxy_server:port
```

### 2. 获取API密钥

1. 访问 [Fish Audio官网](https://fish.audio/)
2. 注册账号并获取API密钥
3. 选择合适的模型ID（如：`eleven_multilingual_v2`）

### 3. 代理配置（可选）

如果您的地区无法直接访问Fish Audio，可以配置代理：

```env
FISH_AUDIO_PROXY_URL=http://127.0.0.1:7890
```

## 使用方式

### 自动触发（LLM判断）

插件会在以下情况下自动触发TTS：

- 用户明确要求使用语音功能
- 对话内容适合用语音传达
- 包含情感表达或需要语音强调的内容
- 较长且适合语音播报的回复
- 故事、诗歌或需要情感渲染的文本

### 手动触发

使用命令手动触发TTS：

```
/fish_audio 你好，这是一段测试文本
```

## 配置选项

插件支持以下配置选项（在`config.toml`中）：

```toml
[plugin]
enabled = true

[components]
enable_fish_audio_tts = true
enable_fish_audio_command = true

[fish_audio]
max_retries = 3
timeout = 30

[fish_audio.voice_settings]
stability = 0.5
similarity_boost = 0.75

[proxy]
enabled = false
url = ""

[logging]
level = "INFO"
prefix = "[Fish Audio TTS]"
```

## 技术特性

### LLM智能判断

插件使用LLM来判断何时触发TTS，确保在合适的时机生成语音：

- **Focus模式**: 使用LLM判断是否适合触发TTS
- **Normal模式**: 同样使用LLM判断，提供一致的体验

### 代理支持

支持HTTP代理，解决网络访问问题：

- 自动检测代理配置
- 支持认证代理
- 连接失败时自动重试

### 错误处理

- 网络超时自动重试
- API错误详细日志
- 优雅的错误提示

## 文件结构

```
plugins/fish_audio_tts_plugin/
├── plugin.py              # 主插件文件
├── _manifest.json         # 插件清单
├── config.toml           # 配置文件
└── README.md             # 说明文档
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查`.env`文件中的`FISH_AUDIO_API_KEY`是否正确
   - 确认API密钥是否有效

2. **网络连接问题**
   - 配置代理URL：`FISH_AUDIO_PROXY_URL=http://your_proxy:port`
   - 检查网络连接是否正常

3. **模型ID错误**
   - 确认`FISH_AUDIO_MODEL_ID`是否正确
   - 检查模型是否可用

### 日志查看

查看插件日志：
```bash
# 在MaiBot日志中搜索
grep "Fish Audio TTS" logs/maibot.log
```

## 开发信息

- **版本**: 1.0.0
- **作者**: MaiBot Community
- **许可证**: MIT
- **依赖**: aiohttp, msgpack

## 更新日志

### v1.0.0
- 初始版本发布
- 支持LLM智能判断触发
- 支持代理配置
- 提供手动命令接口
- 完整的错误处理和重试机制 