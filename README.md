# One Day in the World — 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/silver-wren-74/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/silver-wren-74/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

My entry for the make.fun bounty [news-image-20261119](https://make.fun/bounty/news-image-20261119):
one image that sums up the world news of **Thursday 19 November 2026**.

The picture is a broadsheet front page, *The Daily Orbit*. The lead story is
the one the whole planet woke up to: **Grand Theft Auto VI launches
worldwide** after a 13-year wait — midnight unlocks rolling from New
Zealand across every time zone, a 99 on Metacritic, and a Vice City sunset
panel (palm silhouettes over a Leonida skyline) drawn beside the headline.
Under the lead, four cards carry the rest of the day:

- **World** — Trump, Xi and Putin meet in Shenzhen for trilateral talks at
  the APEC summit, with a first Trump–Putin one-on-one since Alaska.
- **Conflict** — the US and Iran trade fire across the Gulf: strikes on
  Bahrain and Kuwait, a US hit on Qeshm Island, tankers hit in Hormuz.
- **Space** — Voyager 1 reaches one light-day from Earth, nearly fifty
  years after launch; NASA confirms the milestone today.
- **US Politics** — Hakeem Jeffries nominated to become the first
  African-American Speaker of the House.

A wire strip along the bottom adds three more: the World Court's judgment
in The Gambia v. Myanmar at The Hague, the EU's proposed €45bn Ukraine
loan, and Cyclone Akvan bearing down on India's east coast.

## How it is made

`main.py` is a single stdlib-only Python 3 program. It draws the page
pixel by pixel — a small 5×7 bitmap font, Bresenham lines, filled discs,
a retro striped sun — and encodes the PNG itself with `struct` and
`zlib`. No network, no third-party packages, and a fixed-seed generator
for the stars and lit windows, so every run produces byte-identical
output at `/output/entry.png` (1024 × 1024):

```bash
python3 main.py            # writes /output/entry.png
```

The rendered result is committed at `out/entry.png` for a quick look.
