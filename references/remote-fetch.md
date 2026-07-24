# Remote Fetch 协议（Lexmount 云端抓取兜底）

抓取论文/新闻页面（arxiv、ar5iv、Google 检索、公众号等）遇到**限速 / 403 / 反爬 / 动态渲染拿不到正文**时，默认切换到 Lexmount 云端工具，而不是原地重试。

## 工具选择

| 场景 | 命令 |
|:-----|:-----|
| URL 已知，只要正文/结构化内容（首选） | `webfetch-cli extract --url <url>` |
| 需要完整渲染后 DOM | `webfetch-cli dump-dom --url <url>` |
| 需要交互（点击、翻页、登录态、截图） | `browser-cli session create` → `browser-cli action observe` → 语义化动作（click-role / fill-label / get-text-role 等） |

- `extract` 返回 Markdown 摘要（标题、作者、正文、链接），token 开销小，daily-papers / news-digest 场景基本够用。
- browser-cli 临时 session 用完必须关闭。

## 配置（2026-07-24 起双账号）

- **repo Python 脚本**（`scripts/lexmount_fetch.py`、daily-papers `fetch_and_score.py`）：凭据在仓库根 `.env`（已 gitignore）。主账号为 .cn 站：`LEXMOUNT_API_KEY` / `LEXMOUNT_PROJECT_ID` / `LEXMOUNT_BASE_URL=https://api.lexmount.cn`；备用 .com 账号存于 `LEXMOUNT_COM_*` 前缀变量，需要时经环境变量覆盖使用。脚本 base URL 解析链：`LEXMOUNT_WEBFETCH_BASE_URL` → `LEXMOUNT_BASE_URL` → 旧默认主机；并对 api.lexmount.* 端点发送 `x-project-id` 头（必需，缺失返回 400；key 无效返回 401）。
- **CLI 工具**：凭据 `~/.config/lexmount/{browser-cli,webfetch-cli}/credentials.json`（project_id + api_key + `"api_base_url": "https://api.lexmount.com"`，权限 0600），使用 .com 账号。
- **key 与站点绑定，两站凭据不互通**：.cn key 只对 `api.lexmount.cn` 有效，.com key 只对 `api.lexmount.com`。旧主机 `webfetch.lexmount.com` 对两个账号均 401，视为废弃。
- 健康检查：`webfetch-cli auth status`、`browser-cli doctor --json`、`python3 scripts/lexmount_fetch.py extract https://example.com`。
- 凭据失效时到对应站点控制台（browser.lexmount.com / browser.lexmount.cn）重新签发；不要把 API key 粘贴到对话、日志或可提交文件里。

## 使用原则

- 常规可达的页面仍然直接 curl / 本地抓取，云端工具是**兜底**而非默认首跳（有配额）。
- 同一 URL 本地失败一次即可切换，不做多轮本地重试。
