# Fish Audio TTS Plugin for MaiBot

🎵 一个为MaiBot提供Fish Audio语音合成功能的插件，支持随机触发和代理访问。

## 功能特性

- 🎲 **随机触发**: 根据配置的概率随机触发语音合成
- 🌐 **代理支持**: 支持代理访问，解决国内网络访问问题
- 🎯 **智能过滤**: 自动过滤短消息，只对有意义的内容进行语音合成
- 🔄 **重试机制**: 内置重试和指数退避机制，提高成功率
- 💾 **自动保存**: 自动保存生成的语音文件到本地

## 安装要求

### 依赖包

```bash
pip install aiohttp msgpack
```

### 环境变量

在`.env`文件中添加以下配置：

```env
# Fish Audio API配置
FISH_AUDIO_API_KEY=your_api_key_here
FISH_AUDIO_MODEL_ID=your_model_id_here

# 代理配置（可选）
FISH_AUDIO_PROXY_URL=http://127.0.0.1:7890
```

## 配置说明

### 获取API密钥

1. 访问 [Fish Audio](https://fish.audio/go-api/) 注册账号
2. 在控制台创建API密钥
3. 将密钥添加到环境变量

### 获取模型ID

1. 在Fish Audio平台创建或选择一个语音模型
2. 复制模型ID
3. 将模型ID添加到环境变量

### 代理配置

如果在中国大陆使用，可能需要配置代理：

```env
FISH_AUDIO_PROXY_URL=http://127.0.0.1:7890
```

常见的代理配置：
- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809`
- Shadowsocks: `socks5://127.0.0.1:1080`

## 使用方法

### 1. 插件安装

将插件文件夹复制到`src/plugins/`目录下：

```bash
cp -r fish_audio_tts src/plugins/
```

### 2. 配置环境变量

编辑`.env`文件，添加必要的配置：

```env
# Fish Audio配置
FISH_AUDIO_API_KEY=sk-your-api-key-here
FISH_AUDIO_MODEL_ID=model-id-here

# 代理配置（可选）
FISH_AUDIO_PROXY_URL=http://127.0.0.1:7890
```

### 3. 重启MaiBot

重启MaiBot服务，插件将自动加载。

### 4. 测试功能

在群聊中发送消息，插件会随机触发语音合成。

## 配置选项

### 触发概率

在配置文件中调整触发概率：

```toml
[fish_audio_tts]
trigger_probability = 0.1  # 10%触发概率
```

### 语音设置

调整语音生成参数：

```toml
[fish_audio_tts.voice_settings]
stability = 0.5        # 稳定性 (0.0-1.0)
similarity_boost = 0.75  # 相似度提升 (0.0-1.0)
```

### 重试配置

```toml
[fish_audio_tts]
max_retries = 3    # 最大重试次数
timeout = 30       # 超时时间（秒）
```

## 文件结构

```
fish_audio_tts/
├── __init__.py              # 插件初始化文件
├── actions/
│   ├── __init__.py          # Actions包初始化
│   └── fish_audio_action.py # 核心Action类
├── config_template.toml     # 配置模板
└── README.md               # 说明文档
```

## 工作原理

1. **消息监听**: 插件监听所有文本消息
2. **随机触发**: 根据配置的概率决定是否触发
3. **内容过滤**: 过滤掉过短或无意义的消息
4. **API调用**: 使用Fish Audio API生成语音
5. **文件保存**: 将生成的语音保存到本地
6. **消息发送**: 将语音消息发送回群聊

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查`FISH_AUDIO_API_KEY`是否正确设置
   - 确认API密钥是否有效

2. **模型ID错误**
   - 检查`FISH_AUDIO_MODEL_ID`是否正确
   - 确认模型是否存在且可访问

3. **网络连接问题**
   - 检查代理配置是否正确
   - 确认网络连接是否正常

4. **权限问题**
   - 确认`data/audio/fish_audio`目录有写入权限

### 日志查看

查看MaiBot日志以获取详细错误信息：

```bash
tail -f logs/maibot.log | grep "Fish Audio TTS"
```

## 开发说明

### 扩展功能

可以通过继承`FishAudioAction`类来扩展功能：

```python
class CustomFishAudioAction(FishAudioAction):
    async def can_execute(self, message: MaimMessage, **kwargs) -> bool:
        # 自定义触发条件
        return super().can_execute(message, **kwargs)
```

### API参考

- [Fish Audio API文档](https://docs.fish.audio/)
- [MaiBot插件开发文档](https://docs.mai-mai.org/develop/plugin_develop/)

## 许可证

本插件遵循MaiBot的GPL-3.0许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个插件！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持随机触发语音合成
- 支持代理访问
- 内置重试机制 