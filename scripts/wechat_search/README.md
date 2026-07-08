# wechat_search — 公众号文章检索

把微信公众号纳入资讯摄入链路的共享工具。被 `news-digest` 与 `daily-papers` 两个 skill 调用。

## 组成

| 文件 | 作用 |
|------|------|
| `search_wechat.js` | 底层爬虫：爬**搜狗微信搜索**（weixin.sogou.com）按关键词搜文章，返回 JSON（标题/url/摘要/时间/来源公众号）。无需 API key。vendored 自 [zjp1997720/wechat-article-search](https://github.com/zjp1997720/wechat-article-search)（MIT，见 `LICENSE`） |
| `fetch_wechat.py` | 上层封装：读 `team-config.json` `news.wechat`，按中文关键词批量搜、按**关注账号白名单**过滤、按关键词打分 + 时间窗过滤，输出与 news candidates 对齐的 JSON |
| `package.json` | 唯一依赖 `cheerio` |

## 安装（一次）

```bash
cd scripts/wechat_search && npm install   # 需要 Node 18+
```

`node_modules/` 已 gitignore，`git clone` 后需本地重建。

## 用法

```bash
# 底层脚本（调试用）：
node scripts/wechat_search/search_wechat.js "具身智能" -n 5

# 封装（skill 实际调用的）：读 config 关键词 + 账号，输出候选
python3 scripts/wechat_search/fetch_wechat.py --days 3 \
  --output Workbench/daily/.wechat-candidates.json
```

## 设计与约束

- **关键词驱动 + 账号白名单**：搜狗只支持"按关键词搜全网公众号"，没有"列某账号最新文章"模式。
  所以配置里的 `accounts` 当**白名单**——用中文兴趣关键词广撒网，只保留来自关注账号的结果
  （`whitelist_only: true`）。想放宽就把它设 `false`，届时非白名单结果保留但降权排后。
- **公众号是二手线索**：它多在解读论文，真正入库的证据是它指向的**原始论文**（应 digest 原文）。
- **反爬**：搜狗会偶发限流/返空。`fetch_wechat.py` 单关键词失败跳过不阻塞、记入 `errors`；
  查询间有 `query_delay_sec` 延迟。返回的是搜狗中间链，`mp.weixin.qq.com` 真链常解析失败——
  据标题+摘要判断即可。
- **配置**全在 `Workbench/config/team-config.json` 的 `news.wechat`（accounts / keywords /
  per_keyword / max_queries / whitelist_only / query_delay_sec）。
