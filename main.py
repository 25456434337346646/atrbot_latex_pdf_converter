#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import time
import re
import socket
import markdown2
from playwright.async_api import async_playwright
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import File
from astrbot.api import AstrBotConfig

logger = logging.getLogger("astrbot")

@register("astrbot_plugin_latex_pdf_converter", "LaTeX PDF Converter",
          "将含有 LaTeX 公式的消息转换为 PDF 发送", "1.0.0")
class LatexPdfConverterPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config if config is not None else {}
        self.data_dir = "/AstrBot/data/pdf_reports"
        self.http_port = 8765
        os.makedirs(self.data_dir, exist_ok=True)
        asyncio.create_task(self._schedule_cleanup())
        logger.info("[LaTeX PDF Converter] 插件已初始化")

    @filter.after_message_sent()
    async def handle_after_message_sent(self, event: AstrMessageEvent):
        try:
            text = event.message_str
            if not text or not self._has_latex_formula(text):
                return

            logger.info("[LaTeX检测] 检测到公式，准备生成 PDF")
            try:
                pdf_path = await self._generate_pdf(text)
                pdf_result = await self._send_pdf(pdf_path)
                yield event.chain_result(pdf_result)
            except Exception as e:
                logger.error(f"[PDF生成] 失败: {str(e)}", exc_info=True)
                yield event.plain_result(f"PDF 生成失败: {str(e)}")
        except Exception as e:
            logger.error(f"[插件错误] {str(e)}", exc_info=True)

    def _has_latex_formula(self, text: str) -> bool:
        pattern = r'\\\(.*?\\\)|\\\[.*?\\\]'
        return bool(re.search(pattern, text, re.DOTALL))

    def _markdown_to_html(self, text: str) -> str:
        try:
            html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
            return html
        except Exception as e:
            logger.error(f"[Markdown转换] 失败: {e}")
            import html as html_module
            return f"<pre>{html_module.escape(text)}</pre>"

    def _inject_mathjax(self, html: str) -> str:
        mathjax_config = '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},startup:{pageReady:()=>{return MathJax.startup.defaultPageReady().then(()=>{window.MATHJAX_DONE=true;});}}};}</script>'
        mathjax_script = mathjax_config + '<script id="MathJax-script" src="https://npm.elemecdn.com/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>'
        body_css = 'font-family:"Times New Roman",serif;padding:40px;line-height:1.6;color:#333'
        h_css = 'color:#2c3e50;margin-top:20px'
        p_css = 'margin:10px 0'
        code_css = 'background:#f4f4f4;padding:2px 6px;border-radius:3px;font-family:"Courier New",monospace'
        pre_css = 'background:#f4f4f4;padding:10px;border-radius:5px;overflow-x:auto;font-family:"Courier New",monospace'
        bq_css = 'border-left:4px solid #2c3e50;padding-left:10px;margin-left:0;color:#666'
        table_css = 'border-collapse:collapse;width:100%;margin:10px 0'
        td_css = 'border:1px solid #ddd;padding:8px;text-align:left'
        th_css = 'background-color:#f4f4f4'
        full_html = '<!DOCTYPE html><html><head><meta charset="UTF-8">' + mathjax_script + '<style>body{' + body_css + '}h1,h2,h3{' + h_css + '}p{' + p_css + '}code{' + code_css + '}pre{' + pre_css + '}blockquote{' + bq_css + '}table{' + table_css + '}th,td{' + td_css + '}th{' + th_css + '}</style></head><body><div class="content">' + html + '</div></body></html>'
        return full_html

    async def _generate_pdf(self, text: str) -> str:
        try:
            logger.info(f"[PDF生成] 开始处理，文本长度: {len(text)}")
            html = self._markdown_to_html(text)
            full_html = self._inject_mathjax(html)
            pdf_path = os.path.join(self.data_dir, f"report_{int(time.time())}.pdf")
            logger.info(f"[PDF生成] 目标路径: {pdf_path}")

            async with async_playwright() as p:
                logger.info("[PDF生成] 启动 Chromium")
                browser = await p.chromium.launch()
                page = await browser.new_page()
                logger.info("[PDF生成] 设置页面内容")
                await page.set_content(full_html, wait_until="networkidle", timeout=60000)
                logger.info("[PDF生成] 等待 MathJax 完成渲染")
                try:
                    await page.wait_for_function("window.MATHJAX_DONE === true", timeout=30000)
                    logger.info("[PDF生成] MathJax 渲染完成")
                except Exception as e:
                    logger.warning(f"[PDF生成] MathJax 等待超时或失败: {e}，继续导出 PDF")

                await asyncio.sleep(0.5)
                logger.info("[PDF生成] 导出 PDF")
                await page.pdf(path=pdf_path, format="A4")
                await browser.close()

            logger.info(f"[PDF生成] 成功: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"[PDF生成] 失败: {str(e)}", exc_info=True)
            raise

    async def _send_pdf(self, pdf_path: str):
        try:
            pdf_filename = os.path.basename(pdf_path)
            hostname = socket.gethostname()
            if hostname and not hostname.startswith("localhost"):
                http_url = f"http://{hostname}:{self.http_port}/pdf/{pdf_filename}"
            else:
                http_url = f"http://127.0.0.1:{self.http_port}/pdf/{pdf_filename}"

            logger.info(f"[文件发送] URL: {http_url}")
            return [File(name=pdf_filename, url=http_url)]

        except Exception as e:
            logger.error(f"[文件发送] 失败: {str(e)}", exc_info=True)
            raise

    async def _schedule_cleanup(self):
        while True:
            await asyncio.sleep(24 * 60 * 60)
            await self._cleanup_old_files()

    async def _cleanup_old_files(self):
        try:
            current_time = time.time()
            one_day_seconds = 24 * 60 * 60
            cleanup_count = 0

            if os.path.exists(self.data_dir):
                for filename in os.listdir(self.data_dir):
                    filepath = os.path.join(self.data_dir, filename)
                    try:
                        if os.path.isfile(filepath):
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > one_day_seconds:
                                os.remove(filepath)
                                cleanup_count += 1
                                logger.info(f"[文件清理] 已删除: {filename} (年龄: {file_age/3600:.1f}小时)")
                    except Exception as e:
                        logger.warning(f"[文件清理] 删除失败 {filename}: {e}")

            if cleanup_count > 0:
                logger.info(f"[文件清理] 本次清理 {cleanup_count} 个文件")
        except Exception as e:
            logger.error(f"[文件清理] 异常: {e}")
