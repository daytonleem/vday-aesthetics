# vday-aesthetics

Static site for a plastic surgery / aesthetics clinic (GitHub Pages,
custom domain via CNAME).

## AI-generated media

Anything the `/generate` skill (`.claude/skills/generate/`) makes —
images or video — gets saved straight into the `generations/` folder
at the repo root, flat, no subfolders. That's what `gallery.html`
reads, so new generations just show up there on reload. Don't move
or reorganize `generations/` — the skill and the gallery both assume
that exact path.
