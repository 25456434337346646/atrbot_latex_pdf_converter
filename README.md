# AstroBot LaTeX PDF Converter

自动检测消息中的 LaTeX 公式（`\(...\)` 和 `\[...\]`），将含有公式的整段回答转换为精美 PDF 文件发送。

## 功能

- **自动检测**：消息发送后拦截，检测是否含 LaTeX 公式
- **PDF 生成**：Markdown → HTML + MathJax → PDF（Playwright/Chromium 渲染）
- **文件发送**：通过 HTTP 服务器提供 PDF 下载链接
- **自动清理**：超过 24 小时的 PDF 文件自动删除
- **无侵入**：不含公式的消息正常发送，不影响原有流程

## 安装

```bash
# 将插件目录复制到 AstroBot 插件目录
cp -r astrbot_plugin_latex_pdf_converter /AstrBot/data/plugins/
```

## 依赖

- `markdown2`：Markdown 转 HTML
- `playwright`：HTML 渲染为 PDF（需安装 Chromium）
- `aiohttp`：HTTP 文件服务器

AstroBot 会自动安装 `requirements.txt` 中的依赖。

## 启用插件

通过 WebUI `http://<服务器IP>:6185` → 插件管理 → 启用 `astrbot_plugin_latex_pdf_converter`。

## 工作流程

```
消息发送
  → after_message_sent() 钩子拦截
  → 正则检测 \(...\) 或 \[...\]
  → 含公式: Markdown → HTML → MathJax 渲染 → 导出 PDF → 发送文件
  → 不含公式: 正常发送（不干预）
```

## 配置

无需额外配置。插件使用与现有 `astrbot_plugin_multimodal_pdf_router` 共享的：
- PDF 存储目录：`/AstrBot/data/pdf_reports/`
- HTTP 文件端口：`8765`

## 文件结构

```
astrbot_plugin_latex_pdf_converter/
├── main.py              # 核心插件代码
├── manifest.json        # 插件元数据
└── requirements.txt     # Python 依赖
```

## 故障排查

| 问题 | 解决方法 |
|------|---------|
| 插件加载失败 | 检查 `docker logs` 查看错误详情 |
| PDF 生成失败 | 确认 Playwright Chromium 已安装：`playwright install chromium` |
| 文件无法下载 | 确认 HTTP 服务器端口 8765 未被占用 |
| 公式未渲染 | 检查消息中 LaTeX 格式是否为 `\(...\)` 或 `\[...\]` |

## 版本

**v1.0.0** - 初始版本
- LaTeX 公式自动检测
- Markdown → PDF 转换
- HTTP 文件服务器
- 24 小时自动清理
