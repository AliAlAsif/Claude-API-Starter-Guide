# Claude API Starter Guide

A single-page, zero-dependency website that helps beginners get started with the Claude API: setup, token costs, API key safety and prepaid credit tracking, with live cost calculators that work in any currency.

> **Unofficial.** This is a community learning resource. It is not affiliated with or endorsed by Anthropic. Prices and limits change, so always confirm them on the official pages listed in [Sources](#sources).

**Live site:** `https://<your-username>.github.io/<your-repo>/` (see [Deploy](#deploy-to-github-pages))

## Features

- **My credit panel:** enter your currency, the credit you bought, the total you paid (tax and card fees included) and the purchase date. The page computes your effective cost per $1, your expiry date and the days left.
- **Setup instructions** that switch between Windows and macOS/Linux, and between Python, JavaScript and curl, with copy buttons.
- **Three cost calculators:**
  1. One request, priced on all four models side by side.
  2. A chat that resends its history each turn, showing how cost grows.
  3. A budget planner: cost per day and per 30 days, and how long your credit lasts.
- **Custom prices** option, so the calculators keep working if rates change.
- **Concept explainers:** stateless API, tokens, `max_tokens`, context window.
- **API key safety:** expiry facts, safety rules, rotation, and what to do after a leak.
- **Error table** and a pre-flight checklist.
- Light and dark themes, mobile friendly.

## Quick start

No build step and no dependencies. Open the file in a browser:

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
# then open index.html in your browser
```

Or serve it locally:

```bash
python -m http.server 8000
# visit http://localhost:8000
```

## Deploy to GitHub Pages

1. Make sure the page is named `index.html` in the root of the repository.
2. Push it to GitHub.
3. Open the repository's **Settings**, then **Pages**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Choose your main branch and the `/ (root)` folder, then save.
6. After a minute or two the site appears at `https://<your-username>.github.io/<your-repo>/`.

Any static host (Netlify, Vercel, Cloudflare Pages) works the same way: upload `index.html`.

## How the calculators work

```
cost = (input_tokens × input_price + output_tokens × output_price) ÷ 1,000,000
```

Prices are in dollars per million tokens. For a chat that resends its history, with `T` turns, a system prompt of `s` tokens, `u` tokens per question and `r` tokens per reply:

```
total_input  = T × (s + u) + (u + r) × T × (T − 1) ÷ 2
total_output = T × r
```

The quadratic term is why long chats get expensive: turn 10 pays again for turns 1 to 9.

Your effective cost per $1 of credit is `total paid ÷ credit bought`, so taxes and conversion fees are included automatically. The expiry date is the purchase date plus one calendar year.

### Prices used (checked October 2026)

| Model | Model ID | Input | Output |
|-------|----------|-------|--------|
| Haiku 5.5 | `claude-haiku-5-5` | $0.10 | $0.50 |
| Sonnet 5.5 | `claude-sonnet-5-5` | $2.00 | $10.00 |
| Opus 5.5 | `claude-opus-5-5` | $4.00 | $20.00 |
| Fable 5.1 | `claude-fable-5-1` | $10.00 | $50.00 |

USD per million tokens. Haiku 5.5 is charged at a higher rate ($0.50 input, $2.50 output) when a single prompt exceeds 100,000 tokens, and the calculators apply that rule per request.

### Known limits

- Results are **estimates**. You supply the token counts; compare with your Console's Spending page after real calls.
- Batch API discounts and prompt caching are not modeled. Use **Custom prices** to approximate them.

## Customize

Everything lives in `index.html`.

- **Update prices:** edit the `P` object in the script (and the price table in the HTML).
- **Add a model:** add it to `P` and `NM` in the script, and add an `<option>` to the model `<select>`.
- **Change the expiry rule:** edit the `Date.UTC(y+1, ...)` line in the `setts()` function.
- **Colors:** change the CSS variables at the top of the stylesheet. Dark values are defined once for the system setting and once for the manual toggle.

## Privacy

The page makes **no network requests**, loads no external scripts or fonts, and never asks for your API key. Your credit settings are saved only in your browser's `localStorage` on your own device.

## Contributing

Issues and pull requests are welcome, especially for corrected prices, new languages and clearer explanations. Please keep the page dependency-free.

## Sources

- Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Credit terms: https://www.anthropic.com/legal/credit-terms
- API key best practices: https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure

## License

MIT. See `LICENSE`. (Add a `LICENSE` file to your repository, or replace this section with your preferred license.)
