# ElevenLabs: generating the voice

## Access
Preferred: the **ElevenLabs connector** (tools named `mcp__ElevenLabs__creative_*`; load them with
ToolSearch, e.g. query `elevenlabs speech`). It needs no API key. If the tools are missing, ask the
user to connect the ElevenLabs connector in claude.ai (Settings → Connectors) and enable it for the chat.

Fallback: the REST API with a key stored as an **environment secret** named `ELEVENLABS_API_KEY`
(cloud environment settings → API credentials / environment variables) and `api.elevenlabs.io`
added to the allowed domains. A new session is needed before the secret is visible. Never write a
key into files, the skill, commits or chat. If the user pastes a key in chat, tell them to delete it in
ElevenLabs and create a new one. With the API, `POST /v1/text-to-speech/{voice_id}/with-timestamps`
returns character-level timings, which could replace `align_words.py`. That path was never tested
here, so verify the response format on first use.

## Voice
The voice ID changes between projects, so ask for it every time. Never reuse one from memory.
The first status result shows the voice's display name. Mention it so the user can
catch a wrong ID early.

## Models and cost (measured)
| model | use | credits | Swedish speaking rate |
|---|---|---|---|
| `eleven_v4` | final voice in video 2: the user found it the most human, natural pace (a slight echo) | showed 0 in the status results (Sept 2026); check `price` | ~18 chars/s in paragraph takes |
| `eleven_v3` | final voice in video 1 (user's first choice); the most even pitch in paragraph takes, but reads slowly | ~1 per character | ~15 chars/s |
| `eleven_multilingual_v2` | older default; ~13 % faster speech than v3 | ~1 per character | ~19 chars/s |
| `eleven_flash_v2_5` | word-by-word timing reference only | ~0.5 per character | — |
| Voice Isolator (`audio_isolation`) | removes echo/room sound from finished audio | ~1 000 per minute of audio | — |

Pass `estimate_only: true` to price a call before generating. For a 110 s ad, expect about 1 900 credits
for the voice plus about 1 000 for the flash reference. Confirm the model with the user per project.

## Procedure: one take per paragraph, then split into sentences
Reading each sentence as a separate generation made the voice drift: different pitch, stress and
accent from sentence to sentence ("sounds like two people"), and once even a female voice for one
sentence. Reading 6-9 consecutive sentences (400-650 characters) in **one** generation keeps one
consistent performance; `split_takes.py` then cuts it into the per-sentence clips the rest of the
pipeline uses, so anchors and captions work as before.

1. `creative_create_flow` with a descriptive name. Pass its `flow_id` to every later call.
2. Group the script into paragraphs of 6-9 sentences along the story (not across a topic change).
   For each paragraph call `creative_add_flow_node` with `node_type: tts`, the model, `voice_id` from
   the user, `prompt` = the paragraph's sentences from `sent/NN.txt` joined with spaces, and
   **`model_parameters: {"language_code": "sv"}`**. Without the language code the model guesses the
   language per call, which changes the pronunciation. (`creative_generate_speech` cannot set it.)
3. Start the nodes with `creative_run_flow_nodes`, **`generations_count: 1`** (the default is 4, which
   costs 4× as much), at most **5 node ids at a time**: some subscriptions allow only 5 concurrent
   requests, and extra ones come back `status: failed` with "Too many concurrent requests". Those were
   not generated; run exactly those again.
4. Poll `creative_get_flow_run_status` with the `session_ids`. Takes usually finish within 30-60 s.
   Never start a node again to "retry" a take that completed or is still running; that charges again.
5. Copy each `media[].url` exactly into `urls.txt` as `G01 URL` lines and run
   `bash scripts/download_clips.sh urls.txt WORK/takes`. The signed URLs expire after about 2 h.
6. Split each take: `python3 scripts/split_takes.py WORK/takes/G01.mp3 WORK/sent 01 02 ... 09`.
   A `CHECK` line means a comma/colon pause was probably taken for a sentence end: rerun with `--gaps`,
   read the pause list against the text and pass the right boundaries with `--cuts t1,t2,...`.
7. `python3 scripts/tighten_pauses.py WORK/sent` shortens long comma pauses inside sentences
   (> 0.20 s → 0.16 s) before `align_words.py`.
8. The flash word reference: one more call (`creative_generate_speech`, `eleven_flash_v2_5`, same voice)
   with `sent/iso.txt` ("word. word. word."). It is only for timing and never heard. A prompt may be at
   most **5 000 characters**: for a long script split `iso.txt` at a sentence boundary into two prompts
   and join the downloads with ~0.6 s of silence (ffmpeg `concat`) into `sent/iso.mp3`. It depends only
   on the text, so it can be reused when the voice is regenerated with the same script.
9. To fix one sentence later, regenerate its whole paragraph take (a lone sentence will not match the
   voice of its neighbours), then split and tighten again.

Check the result for odd sentences: median pitch per clip (librosa `pyin`) should stay within about
±15 Hz of the voice's median; a clip far above it (e.g. 157 Hz with peaks at 270 Hz for a ~110 Hz
male voice) is a different voice and its take must be regenerated.

## Why not one long take of the whole script
One take of 5 minutes cannot be split or synced reliably, and a regenerated fix would change everything.
Paragraph takes keep the voice consistent while every sentence still gets an exact start and end, and
the planner can still move sentences onto visuals and set tempo per section.

## Things that do not work
- `creative_transcribe_audio` (Scribe) through the connector returns plain text with **no timestamps**,
  so it is useless for syncing.
- Downloading speech-recognition models (Whisper and similar) is blocked in the cloud sandbox. That is
  why `align_words.py` combines three model-free methods.

## Writing text for TTS
- Punctuation drives the pauses. A comma gives a short pause, "…" a longer one.
- Write numbers and symbols as words: "fyra komma åtta av fem", "sextio dagars", "femtio procent".
- If a brand name is mispronounced, spell it phonetically in the TTS text only, and keep the correct
  spelling for the captions by editing `NN.txt` after generation.
- eleven_v3 and eleven_v4 understand audio tags like `[excited]`. Use them sparingly; they are rarely needed for ads.
