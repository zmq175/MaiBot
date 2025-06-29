# Fish Audio TTS Plugin for MaiBot

Fish Audio TTS插件为MaiBot提供高质量的文本转语音功能，支持LLM智能判断和代理访问。

## 功能特性

- 🎵 **高质量语音合成**：使用Fish Audio API生成自然流畅的语音
- 🤖 **LLM智能判断**：在Focus模式下由LLM智能判断何时触发TTS
- 🎲 **概率触发**：在Normal模式下使用概率触发机制（默认15%）
- 🌐 **代理支持**：支持代理配置，解决部分地区访问问题
- 📝 **手动触发**：支持通过命令手动触发TTS功能
- ⚙️ **灵活配置**：提供丰富的配置选项

## 触发机制

### Focus模式
- 使用LLM智能判断，根据对话内容和上下文决定是否触发TTS
- 提供详细的LLM判断提示词，确保触发时机准确

### Normal模式
- 由于性能考虑，LLM_JUDGE类型会被转换为概率触发
- 默认触发概率为15%，可通过配置调整
- 触发概率范围：0.0-1.0（0%到100%）

### 手动触发
- 使用命令：`/fish_audio <文本内容>`
- 例如：`/fish_audio 你好，这是一条测试语音消息`

## 安装配置

### 1. 环境变量配置

在MaiBot根目录的`.env`文件中添加以下配置：

```env
# Fish Audio API配置
FISH_AUDIO_API_KEY=your_api_key_here
FISH_AUDIO_MODEL_ID=your_model_id_here

# 可选：代理配置（如果需要）
FISH_AUDIO_PROXY_URL=http://your_proxy_url:port
```

### 2. 插件配置

插件配置文件：`plugins/fish_audio_tts_plugin/config.toml`

```toml
[plugin]
enabled = true

[components]
enable_fish_audio_tts = true
enable_fish_audio_command = true

[fish_audio]
max_retries = 3
timeout = 30
random_activation_probability = 0.15  # Normal模式触发概率

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

### 3. 配置说明

#### 核心配置
- `random_activation_probability`: Normal模式下的触发概率（0.0-1.0）
- `max_retries`: API调用最大重试次数
- `timeout`: API调用超时时间（秒）

#### 语音设置
- `stability`: 语音稳定性（0.0-1.0），值越高语音越稳定
- `similarity_boost`: 相似度提升（0.0-1.0），值越高越接近目标声音

#### 代理配置
- `enabled`: 是否启用代理
- `url`: 代理服务器URL

## 使用示例

### 自动触发
在聊天中，插件会根据以下情况自动触发：
- 用户明确要求语音回复
- 对话内容适合语音表达
- 情感表达需要语音强调
- 长文本内容适合语音播报

### 手动触发
```
/fish_audio 这是一条测试语音消息
/fish_audio 请用语音读一下这首诗
```

## 注意事项

1. **API密钥安全**：请妥善保管Fish Audio API密钥，不要泄露
2. **网络访问**：确保能够访问Fish Audio API，必要时配置代理
3. **触发频率**：Normal模式下建议保持较低的触发概率，避免过度使用
4. **音频存储**：生成的音频文件会保存在`data/audio/fish_audio/`目录下

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 验证模型ID是否有效

2. **代理连接问题**
   - 检查代理URL格式是否正确
   - 确认代理服务器可访问
   - 验证代理认证信息

3. **触发概率过低**
   - 调整`random_activation_probability`配置
   - 在Focus模式下使用LLM判断更精确

## 更新日志

### v1.0.0
- 初始版本发布
- 支持Fish Audio API集成
- 实现LLM智能判断和概率触发
- 添加代理支持和手动触发功能 