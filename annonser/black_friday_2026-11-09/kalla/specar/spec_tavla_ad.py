import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "tavla_txt.png").as_uri()
ADS = [{"out": "../ut_bf/BF_05_bokstavstavla_4x5.png", "w": 1080, "h": 1350, "css": f"body{{background:#ddd url('{BG}') center top/cover no-repeat}}", "body": ""}]
