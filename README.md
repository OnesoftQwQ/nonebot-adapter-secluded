# nonebot-adapter-secluded

Nonebot2 Secluded 适配器

通过将 Nonebot2 伪装成一个 Secluded 的插件来在 Nonebot2 中运行插件

~~写得比较史不过能用~~ 使用遇到问题欢迎提Issues或PR, 我能解决的尽量解决

目前已知Bug: 有时候会莫名其妙弹 `IndexError: list index out of range`, 我还没能找到原因, 不影响使用

## 使用

从 Releases 中下载最新的 .whl 文件, 然后在你 bot 的虚拟环境中使用 pip 安装即可

安装好适配器后在配置文件(.env文件)中加入

```config
secluded_host=Websocket地址(例如ws://127.0.0.1:1234)
secluded_token=你的token
```

然后启动 Nonebot2 即可使用