# Claude API Starter Guide

A single-page, zero-dependency website that helps beginners get started with the Claude API: setup, token costs, API key safety and prepaid credit tracking, with live cost calculators that work in any currency. Prices update through a weekly pull request.

> **Unofficial.** This is a community learning resource. It is not affiliated with or endorsed by Anthropic. Prices and limits change, so always confirm them on the official pages listed in [Sources](#sources).

**Live site:** https://alialasif.github.io/Claude-API-Starter-Guide/ 

## Features

- **My credit panel:** enter your currency, the credit you bought, the total you paid (tax and card fees included) and the purchase date. The page computes your effective cost per $1, your expiry date and the days left.
- **Setup instructions** that switch between Windows and macOS/Linux, and between Python, JavaScript and curl, with copy buttons.
- **Three cost calculators:** one request on every model, a chat that resends its history, and a budget planner.
- **Custom prices** option, in case you want to test other rates.
- **Concept explainers**, API key safety rules, an error table and a pre-flight checklist.
- Light and dark themes, mobile friendly.
- **Automatic price checks:** a weekly GitHub Actions job compares `prices.json` with Anthropic's pricing page and opens a pull request when something changed.

## Project layout

```
index.html                         the whole website
prices.json                        model prices (the only place prices live)
scripts/update_prices.py           reads Anthropic's pricing page, updates prices.json
.github/workflows/update-prices.yml   weekly schedule and pull request
```

## Quick start

No build step and no dependencies.

```bash
git clone https://github.com/AliAlAsif/Claude-API-Starter-Guide.git
cd Claude-API-Starter-Guide
python -m http.server 8000
# visit http://localhost:8000
```

If you open `index.html` directly from your disk, the browser blocks loading `prices.json`, so the page uses the built-in fallback prices and says so in the Prices section. Serving it as above (or using GitHub Pages) loads `prices.json`.

## Automatic price updates

How it works: every Monday at 06:00 UTC the **Update prices** workflow runs `scripts/update_prices.py`. The script downloads the Markdown version of Anthropic's pricing page, finds the row for each model in `prices.json`, and compares the base input and output prices. If any price differs, the workflow opens a pull request that changes only `prices.json`. Merging it updates the live site.

It deliberately opens a pull request instead of committing directly, so you can compare the numbers with the official page before they go live.

### One-time setup

1. Add the files from this repository, including the hidden `.github` folder.
2. Open **Settings**, then **Actions**, then **General**, scroll to **Workflow permissions**, choose **Read and write permissions**, tick **Allow GitHub Actions to create and approve pull requests**, and save.
3. Open the **Actions** tab, choose **Update prices**, click **Run workflow**, and read the log. It prints the row it matched for every model, so you can confirm the script reads the page correctly.

### What to expect

- **No change:** the run finishes quietly and no pull request is opened.
- **Prices changed:** a pull request titled "Update Claude API prices" appears with an old and new table. Compare it with the official page, then merge.
- **The workflow fails:** the script could not find a model row, usually because the page layout or a model name changed. GitHub emails you. Edit the `match` patterns in `prices.json` (or update the prices by hand).
- **Not checked automatically:** the Haiku long-context rate (`long_context` in `prices.json`) and the "best for" text. Check them yourself when a pull request arrives.
- GitHub disables scheduled workflows in a public repository after 60 days without any repository activity. Merging a price pull request counts as activity. If the schedule stops, re-enable it in the **Actions** tab.

## How the calculators work

```
cost = (input_tokens × input_price + output_tokens × output_price) ÷ 1,000,000
```

Prices are in dollars per million tokens and come from `prices.json`. For a chat that resends its history, with `T` turns, a system prompt of `s` tokens, `u` tokens per question and `r` tokens per reply:

```
total_input  = T × (s + u) + (u + r) × T × (T − 1) ÷ 2
total_output = T × r
```

The quadratic term is why long chats get expensive: turn 10 pays again for turns 1 to 9.

Your effective cost per $1 of credit is `total paid ÷ credit bought`, so taxes and conversion fees are included automatically. The expiry date is the purchase date plus one calendar year.

**Known limits:** results are estimates because you supply the token counts. Batch API discounts and prompt caching are not modeled, so use **Custom prices** to approximate them.

## Customize

- **Change or add a model:** edit `prices.json`. Each model has `key`, `name`, `id`, `input`, `output`, `best` and a `match` list of regular expressions the updater uses to find its row on the pricing page. The page builds its model menu and price table from this file.
- **Built-in fallback prices:** the `DEF` object near the top of the script in `index.html` is used when `prices.json` cannot be loaded. Keep it roughly in sync.
- **Change the expiry rule:** edit the `Date.UTC(y+1, ...)` line in the `setts()` function.
- **Colors:** change the CSS variables at the top of the stylesheet.
- **Change the schedule:** edit the `cron` line in `.github/workflows/update-prices.yml`.

## Privacy

The page loads no third-party scripts, fonts or data and never asks for your API key. Its only network request is for `prices.json` from the same site. Your credit settings are saved only in your browser's `localStorage` on your own device.

## Contributing

Issues and pull requests are welcome, especially for corrected prices, new languages and clearer explanations. Please keep the page dependency-free.

## Sources

- Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Credit terms: https://www.anthropic.com/legal/credit-terms
- API key best practices: https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure

## License

MIT. See [LICENSE](LICENSE).
