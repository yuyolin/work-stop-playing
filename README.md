# 工作！！别他妈玩了！

一个极简的 Windows 本地工作计时器：开始工作、暂停休息、记录上一次工作时长，并提供独立倒计时。

## 功能

- 工作正计时，从 `00:00:00` 开始
- `继续工作` / `休息一下` 一键切换
- 最小化、切换到其他程序时继续计时
- 使用单调时钟计算经过时间，不依赖北京时间
- 保存上一次工作时长
- 最近 100 条工作记录保存在本机 `%APPDATA%\\工作别玩了\\history.json`
- 自定义小时 / 分钟 / 秒倒计时
- 倒计时支持开始、暂停、继续、重置
- 倒计时结束弹窗 + 系统提示音
- 自定义 Windows 程序图标

## 直接运行源码

需要 Python 3：

```bash
python app.pyw
```

## Windows 一键打包 EXE

双击：

```text
BUILD_EXE.bat
```

脚本会安装/检查 PyInstaller，并生成：

```text
dist/工作！！别他妈玩了！.exe
```

同时会尝试把生成的 EXE 复制到 Windows 桌面。

## GitHub Actions 自动构建

仓库包含 Windows 构建工作流。每次推送或手动运行工作流时，GitHub 会在 Windows Runner 上打包 EXE，并将成品作为 Artifact 上传。

## 项目结构

```text
.
├── app.pyw
├── build_app.py
├── BUILD_EXE.bat
├── icon.png
├── icon.ico
├── .github/workflows/build-windows.yml
├── .gitignore
├── LICENSE
└── README.md
```

## License

MIT License。
