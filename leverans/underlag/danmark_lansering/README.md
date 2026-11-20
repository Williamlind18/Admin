# Verktyg: danska lanseringsannonser

Skript från de danska versionerna av lanseringsannonserna (A5 C4, A5 C5, A3 C1, A5 C1, A1 C4 i omgång 1). De körs från
en arbetsmapp med `vid/<nyckel>.mp4` (svensk leverans), `clean/<nyckel>_clean.mp4` (Vmake SKM0002), `music/<nyckel>.mp3`,
`work/<nyckel>/` (röst, ordtider, undertexter) och `ov/<nyckel>/` (danska skyltar).

- `ocr_scan.sh`, `diff_regions.py`, `cap_left.py`: hitta svensk text som är kvar efter Vmake.
- `track.py`, `span.py`, `label_geom.py`: när och var varje skylt syns (per bildruta).
- `build_ov_da.py`: de danska skyltarna, korten och slutbilderna (+ `spec.json` med tider).
- `preview_ov.py`: QA-ark, svensk källa bredvid dansk version.
- `numbers_da.py`, `pairs_da.py`, `measure_caps.py`: siffror och par i undertexterna, undertexthöjd.
- `mix_render2.py`: röst + musik på svensk nivå, loudnorm, rendering med skyltar och undertexter.

Från omgång 2 bygger vi på originalfilmerna i GitHub-releaserna i stället för Vmake (`orig/<nyckel>.mp4`):

- `added.py`, `framemap.py`, `thumbmatch.py`: vad den svenska versionen lade till eller klippte om, jämfört med
  originalet (diff utanför undertextbandet, och bildruta för bildruta vilken originalruta som visas).
- `relabel.py`: bygger om en vit svensk skylt på ett annat språk, ruta för ruta (läge, storlek, vinkel och
  textstorlek från den svenska). `--base` väljer en annan textfri film än originalet.
- `retext.py`: byter bara orden på en skylt som sitter på ett vitt föremål (svensk utsnitt + nya ord).
- `title_box.py`: en stillastående rubrikruta i samma storlek och med samma textstorlek som den svenska.
- `capmasks.py`, `textmasks.py`, `pillmasks.py`: masker för inbrända undertexter till LaMa (`lama_inpaint.py` i
  ad-video-localizer): vita rutor med svart text, vit text med svart kant, och vita textrutor på ljus bakgrund (hittas
  på de vita kanterna ovanför och under texten).
- `measure_box.py`: läge och textrader för en stillastående svensk skylt (till `title_box.py`).
- `assemble_a3c4.py`: exempel på ren film när den svenska versionen bytt ut ett klipp och saktat ner ett annat.
- `bedmap.py`: hur den svenska musiken ligger (linjär, loop, hopp eller förskjuten) så att den danska får samma.
- `make_captions_da.py`: undertexterna (1–3 ord). Varje fras delas med en liten sökning: inte sluta på småord,
  bryt vid kolon, håll ihop tidsuttryck ("Dagene efter", "Næste morgen", "et år siden").
- `rerender.sh`: rendera om och gör små förhandsvisningar (högst cirka 10 MB per del, H.264 Main).
