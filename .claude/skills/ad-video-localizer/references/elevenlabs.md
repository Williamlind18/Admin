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
| `eleven_v3` | final voice (user's choice, most natural) | ~1 per character | ~16 chars/s |
| `eleven_multilingual_v2` | older default; ~13 % faster speech | ~1 per character | ~19 chars/s |
| `eleven_flash_v2_5` | word-by-word timing reference only | ~0.5 per character | — |

Pass `estimate_only: true` to price a call before generating. For a 110 s ad, expect about 1 900 credits
for the voice plus about 1 000 for the flash reference.

## Procedure
1. `creative_create_flow` with a descriptive name. Pass its `flow_id` to every later call.
2. One `creative_generate_speech` per sentence, using the text of `sent/NN.txt` verbatim,
   `model_id: eleven_v3`, `voice_id` from the user and **`generations_count: 1`**. The default is 4,
   which costs 4× as much. Fire up to ~13 calls in one message; they run in parallel.
   Some subscriptions allow only **5 concurrent requests**. Extra calls then come back with
   `status: failed` and "Too many concurrent requests" in the status result. Those were not
   generated, so generate exactly those sentences again, at most 5 at a time.
3. One more call with `eleven_flash_v2_5`, the same voice, and the whole of `sent/iso.txt` as the prompt
   ("word. word. word."). This is only the timing reference and is never heard in the video. Save it as
   `sent/iso.mp3`. A prompt may be at most **5 000 characters**. For a long script, split `iso.txt` at a
   sentence boundary into two prompts, then join the two downloads with ~0.6 s of silence in between
   (ffmpeg `concat`) into `sent/iso.mp3`.
4. Poll `creative_get_flow_run_status` with the `session_ids`, up to ~14 per call. Clips usually finish
   within 30 s. Never call generate again to "retry" a clip that completed or is still running, because
   that charges again.
5. Copy each `media[].url` exactly into a `urls.txt` file as `NN URL` lines (and `iso URL`). Then run
   `bash scripts/download_clips.sh urls.txt WORK/sent`. The URLs are signed storage.googleapis.com links
   that expire after about 2 h. Poll again for fresh ones.
6. If you later rewrite sentence NN: rerun `split_script.py` (it renames the stale clip), generate NN again,
   and also generate a small flash reference of just that sentence's words ("ord. ord.") saved as
   `sent/isoNN.mp3`.

## Why sentence-by-sentence
One long take of the whole script cannot be synced reliably. Sentence boundaries hide inside the audio,
and every timing method drifts by up to a second. Separate clips make every sentence start and end
exact. They also let the planner move sentences onto visuals and set tempo per section.

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
- eleven_v3 understands audio tags like `[excited]`. Use them sparingly; they are rarely needed for ads.
