# Getting files in and out

## Receiving the video
Cloud sandbox: many hosts are blocked (Dropbox, Google Drive and WeTransfer were all blocked). The
reliable channel is the GitHub repo attached to the session.
- **≤ 25 MB:** in the repo on github.com, use Add file → Upload files → Commit changes. Then
  `git fetch origin main` and `git show origin/main:FILE > WORK/src.mp4`.
- **> 25 MB (normal for 1080p exports):** use a **release**, which takes up to 2 GB per file.
  Steps for the user: `https://github.com/OWNER/REPO/releases/new` → Choose a tag (e.g. `video1`) →
  Create new tag → drag the file into "Attach binaries" → Publish release. To add a file later, open the
  release and click the pencil → attach → Update release.
  Download it with:
  `curl -s https://api.github.com/repos/OWNER/REPO/releases` (lists asset URLs), then
  `curl -sSL -o WORK/src.mp4 https://github.com/OWNER/REPO/releases/download/TAG/FILE`
- **Check that it is really the new file.** Users often attach the old file by mistake. Compare
  size or `sha1sum` with the previous source, and run `analyze_video.py --reference OLD.mp4` to see
  what changed.
- Remind the user once that a public repo makes everything uploaded there public.
- WhatsApp-forwarded videos are compressed to ~480p. Ask for the original export if quality matters.

## Returning results
- The chat file tool (SendUserFile) accepts ≤ 30 MB per file. Send `preview.mp4` (render.py makes it
  ≤ 28 MB) plus the `.srt` and the final script as a `.txt`.
- Commit the full-quality mp4 (≤ 100 MB) to the session's working branch together with the `.srt` and
  script, push it, and give the user the GitHub link to the file. They download it with the download
  button on that page.
- Longer videos pass 100 MB at render.py's crf 21 (4:05 came out at about 155 MB). Then make a
  two-pass copy at ~95 MB for GitHub: video kb/s = 95·8·1024 / seconds − 212, `-preset slow -pass 1/2`,
  AAC audio at 192k, `-movflags +faststart`. Say in the report that GitHub caps files at 100 MB.
- **The user wants the best quality on GitHub** (2026-11-02), even when crf 21 is well under 100 MB.
  Make the GitHub copy with `scripts/hq_encode.sh SRC captions.ass fonts final.mp4 OUT.mp4`: a two-pass
  encode at ~95 MB, straight from the source, with final.mp4's mixed audio copied as is.
- Never commit secrets. The repo may be public.

## Final report to the user (write it in their language; Swedish example)
Keep it short and concrete:
1. Where the files are: the preview here, the full quality on GitHub (link).
2. What changed compared with last time or the request: voice model, pauses, script changes.
3. Any timing trade-offs: lines moved, extras dropped because they didn't fit, how much faster
   each part runs ("första delen ca 6 % snabbare, erbjudandet i slutet ca 11 %").
4. Warnings: no background music (unless a music file was supplied), other brands visible in the
   footage, burned-in original text that stays.
5. Credits used in ElevenLabs (add up `price.credits` from the status results), plus the flow link.
6. An invitation to point out any caption that's off. You cannot listen, so they are the final check.
