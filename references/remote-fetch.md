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

## 配置

- 凭据：`~/.config/lexmount/{browser-cli,webfetch-cli}/credentials.json`（project_id + api_key，权限 0600）。
- **端点必须是 `https://api.lexmount.com`**（写在 credentials.json 的 `api_base_url` 字段）。CLI 内置默认值是 `api.lexmount.cn`，对本账号返回 Unauthorized——账号注册在 browser.lexmount.com（.com 站），两站凭据不互通。
- 健康检查：`webfetch-cli auth status`、`browser-cli doctor --json`。
- 凭据失效时到 https://browser.lexmount.com 控制台重新签发；不要把 API key 粘贴到对话里。

## 使用原则

- 常规可达的页面仍然直接 curl / 本地抓取，云端工具是**兜底**而非默认首跳（有配额）。
- 同一 URL 本地失败一次即可切换，不做多轮本地重试。
