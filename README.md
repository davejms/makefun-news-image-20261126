# The world in one page — 26 November 2026

Entry for the make.fun bounty **"Sum up 26 November's world news in one image"**
(`news-image-20261126`).

## What it is

`main.py` is a deterministic, standard-library-only Python 3.13 program.
It draws a one-page newspaper front page summarising eight verified
news stories from Thursday 26 November 2026 and writes it as a single
1024x1024 PNG.

## Run it

```sh
python3 main.py
```

It writes `./.makefun/output/output.png` (1024x1024, at most 1 MiB).
Running it twice produces byte-identical output: no network, no
randomness, no clocks.

## The eight stories

1. **Kuwait** — Iranian drones hit a vital site; two Italian workers killed.
2. **Gaza** — Israeli strikes have killed at least 16 schoolchildren in November.
3. **Ukraine** — Russian drone strikes hit regions and energy facilities.
4. **Global shipping** — UNCTAD: container shipping volumes will not grow in 2026.
5. **Egypt** — Fuel tanker fire on a highway near Cairo kills at least 31.
6. **Thailand** — Major fire at a Bangkok oil depot; a diesel vessel sank.
7. **DR Congo** — Ebola cases pass 12,000.
8. **United States** — Stormy Thanksgiving batters both coasts.

Sources: Al Jazeera, The Guardian, UN News, Euronews, PBS NewsHour.

## Verification

Every push runs `.github/workflows/build.yml`: it runs `main.py` on
Python 3.13, checks the output is a 1024x1024 PNG of at most 1 MiB,
and uploads it as an artifact.

## Licence

MIT — see `LICENSE`.
