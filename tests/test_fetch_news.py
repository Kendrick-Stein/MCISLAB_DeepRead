import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "1-literature" / "news-digest"))
from fetch_news import parse_feed, score_item

RSS2 = """<?xml version="1.0"?>
<rss version="2.0"><channel><title>Blog</title>
<item><title>New GUI agent benchmark released</title>
<link>https://x.test/a</link>
<description>A benchmark for computer-use agents.</description>
<pubDate>{date}</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Blog</title>
<entry><title>Quantum knitting</title>
<link href="https://x.test/b"/>
<summary>Nothing relevant.</summary>
<updated>{date}</updated></entry>
</feed>"""


def test_parse_rss2_and_atom():
    now = datetime.now(timezone.utc)
    items = parse_feed(RSS2.format(date=now.strftime("%a, %d %b %Y %H:%M:%S +0000")))
    assert items[0]["title"] == "New GUI agent benchmark released"
    assert items[0]["link"] == "https://x.test/a"
    assert items[0]["published"] is not None
    items = parse_feed(ATOM.format(date=now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    assert items[0]["link"] == "https://x.test/b"


def test_score_counts_keyword_hits():
    kws = ["gui agent", "computer-use", "vlm"]
    hit = {"title": "New GUI agent benchmark", "summary": "for computer-use agents"}
    miss = {"title": "Quantum knitting", "summary": "nothing"}
    assert score_item(hit, kws) == 2
    assert score_item(miss, kws) == 0
