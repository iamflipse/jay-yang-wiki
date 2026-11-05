# Jay Yang Wiki

A curated wiki on Jay Yang, built from his "Full Courses" trilogy (transcripts) and X posts.

**Public copy:** https://iamflipse.github.io/jay-yang-wiki/ (read-only; static build served from the `gh-pages` branch)

## Layout

- `src/` — wiki pages as markdown (`index.md`, `about.md`, `concepts/`, `sources/`)
- `book/` — mdbook-generated static site (committed for GitHub Pages)
- `tools/mdbook` — mdbook v0.4.21 binary (aarch64 Linux, built from source)
- `tools/transcribe.py` — faster-whisper transcription tool (used to make `src/sources/*-transcript.md`)

## Rebuild + republish

```sh
./tools/mdbook build -d book
cp -r src/sources/media book/    # the X-post photo
git add -A && git commit -m "update" && git push origin main
# republish gh-pages: check out orphan branch, move book/* to root, force push
```
