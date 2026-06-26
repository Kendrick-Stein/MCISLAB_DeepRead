# YAML Frontmatter Validation

This repository includes automated validation for YAML frontmatter in all markdown files to prevent build failures.

## Lexmount Fetch Fallback

`scripts/lexmount_fetch.py` is a no-dependency helper for paper retrieval when normal web access stalls or returns incomplete content.

```bash
export LEXMOUNT_API_KEY="..."
python3 scripts/lexmount_fetch.py extract "https://arxiv.org/html/2604.06126" --format markdown
python3 scripts/lexmount_fetch.py dump "https://arxiv.org/html/2604.06126" --engine lightmount_domstable --format text
```

Do not commit API keys. `.env` is ignored and can be used for local credentials. See `references/network-fetch-fallback.md`.

## Validation Points

### 1. Pre-commit Hook (Local)
A Git pre-commit hook automatically validates YAML before each commit:
```bash
# Hook location: .git/hooks/pre-commit
# Runs: python3 scripts/validate-yaml.py
```

If validation fails, the commit is blocked with error details.

### 2. GitHub Actions (CI/CD)
The deployment workflow validates YAML before building:
```yaml
# File: .github/workflows/deploy.yml
- name: Validate YAML frontmatter
  run: python3 scripts/validate-yaml.py
```

If validation fails, the deployment is aborted.

## Common Issues & Fixes

### Issue: Title contains colon
**Error:** `mapping values are not allowed here`

**Cause:** YAML interprets colons as key-value separators.

**Bad:**
```yaml
---
title: MIRAGE: Mobile Agents with Implicit Reasoning
---
```

**Good:**
```yaml
---
title: "MIRAGE: Mobile Agents with Implicit Reasoning"
---
```

**Fix:** Always quote titles containing colons, commas, or special characters.

### Issue: Multi-line values without proper formatting
**Bad:**
```yaml
description: This is a very long
description that spans multiple lines
```

**Good:**
```yaml
description: "This is a very long description that spans multiple lines"
# OR
description: |
  This is a very long
  description that spans multiple lines
```

## Manual Validation

Run validation manually anytime:
```bash
python3 scripts/validate-yaml.py
```

Output:
- ✅ Success: All files valid
- ❌ Failure: Lists files with errors

## Setup Pre-commit Hook (if missing)

The hook should be created automatically, but if missing:
```bash
chmod +x .git/hooks/pre-commit
```

## Disable Pre-commit Hook (emergency only)

If you need to bypass validation temporarily:
```bash
git commit --no-verify
```

**Warning:** This skips validation and may cause CI/CD failures.
