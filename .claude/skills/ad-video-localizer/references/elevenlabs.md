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

The connector exposes **no voice settings** for eleven_v3 or multilingual_v2: no stability, seed,
similarity or speed (the model schema only has `voice_id` and `language_code`). Consistency
therefore has to come from how the audio is generated, which means **one take**.

## Models and cost (measured)
| model | use | credits | Swedish speaking rate |
|---|---|---|---|
| `eleven_v3` | final voice (user's choice, most natural) | ~1 per character | ~15.5-16 chars/s |
| `eleven_multilingual_v2` | older default; ~13 % faster speech | ~1 per character | ~19 chars/s |
| `eleven_flash_v2_5` | word-by-word timing reference only | ~0.5 per character | — |
| `eleven_v4` | offered by the connector, **untested** here | ? | ? |

**The speaking rate depends on the voice.** The eleven_v3 rate above was measured with the female voice
of the first projects. On Maskinrent video 3 ("UV-testet") the voice "Äldre man 1" read at only
**~13.9 chars/s**. A script budgeted at 16.3 chars/s came back as a 149 s take for a 101.6 s video and had
to be shortened and taken again, which wasted about 1 700 credits. With a voice you have not measured,
generate the first 3-4 lines once with eleven_v3 (~150-250 credits) and divide their characters by the
seconds of speech. Then pass that rate as `split_script.py --rate R`. If the voice was used in an earlier
project, use the rate measured there.

Pass `estimate_only: true` to price a call before generating. For a 135 s ad (≈2 100 characters),
expect about 2 100 credits for the voice take plus about 1 200 for the flash reference.

## Procedure
1. `creative_create_flow` with a descriptive name. Pass its `flow_id` to every later call.
2. **The voice: one take of the whole script.** Call `creative_generate_speech` once with every line
   of `script.txt` joined with single spaces as the prompt, `model_id: eleven_v3`, the user's
   `voice_id` and **`generations_count: 1`**. The default is 4, which costs 4× as much. A 2 141-character
   script was accepted in one call. It took about 2 minutes to generate and came back as 158.6 s of
   audio, sentence pauses included.
3. **The timing reference.** One call with `eleven_flash_v2_5`, the same voice, and the whole of
   `sent/iso.txt` as the prompt ("word. word. word."). This is only the timing reference and is never
   heard in the video. Save it as `sent/iso.mp3`.
4. Poll `creative_get_flow_run_status` with the `session_ids`. For the long take, wait between polls,
   e.g. with a background `until`-loop of ~45 s, instead of polling every few seconds. Never call
   generate again to "retry", because that charges again.
5. Copy each `media[].url` exactly into a urls file (`take URL`, `iso URL`) and download with
   `bash scripts/download_clips.sh urls.txt DIR`. The URLs are signed storage.googleapis.com links that
   expire after about 2 h. Poll again for fresh ones.
6. Cut the take into sentences: `python3 scripts/split_take.py WORK/take.mp3 WORK/sent`. It picks the
   sentence pauses with dynamic programming, using syllable counts as the length guide, and writes
   `sent/NN.mp3`. In the tested take every sentence pause was 0.42-0.78 s and comma pauses were shorter.
   The first version of the splitter cut at a 0.30 s comma pause, which is why long pauses now weigh
   much more. Check the printed table: no row should be marked `<-- check`.
7. If you must change a sentence after the take, see "Changed sentences" in SKILL.md. The best option is
   a new whole take. A separately generated sentence will not sound like the same speaker. Give a
   changed sentence its own word reference, a small flash take of its words ("ord. ord.") saved as
   `sent/isoNN.mp3`.

## Why one take (not one clip per sentence)
The first two videos were built from one eleven_v3 generation per sentence. The user heard the result
as robotic and uneven, "like two different people": each call varies timbre, stress and pronunciation.
One take of the whole script keeps one speaker and a natural flow from sentence to sentence.
It also speaks slightly faster. The same 2 103 characters were 135.5 s of speech as one take, against
140.4 s as 39 clips, so less speed-up is needed. Syncing still works because the take is cut into
sentences at its pauses, and each sentence is then aligned and placed on its own exactly as before.

## Concurrency and failures
The user's subscription allows **5 concurrent requests**. More parallel calls come back with
`status: failed` and "Too many concurrent requests". With one take plus the flash reference this no
longer matters. If you do run many generations, start at most 5 at a time, and re-run only the ones
that failed.

## Things that do not work
- `creative_transcribe_audio` (Scribe) through the connector returns plain text with **no timestamps**,
  so it is useless for syncing.
- Downloading speech-recognition models (Whisper and similar) is blocked in the cloud sandbox. That is
  why `align_words.py` combines three model-free methods.
- Speeding the voice up with the **rubberband** filter. It sounded robotic to the user. `atempo` is
  the default in `build_voiceover.py`.

## Writing text for TTS
- Punctuation drives the pauses. A comma gives a short pause, "…" a longer one. Full stops give the
  clear 0.4-0.8 s pauses that `split_take.py` needs, so keep one sentence per line in `script.txt` and
  end each one with `.`, `?` or `!`.
- Write numbers and symbols as words: "fyra komma åtta av fem", "sextio dagars", "femtio procent".
- If a brand name is mispronounced, spell it phonetically in the TTS text only, and keep the correct
  spelling for the captions by editing `NN.txt` after generation.
- eleven_v3 understands audio tags like `[excited]`. Use them sparingly; they are rarely needed for ads.
