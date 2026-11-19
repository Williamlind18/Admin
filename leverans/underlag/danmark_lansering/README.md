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
