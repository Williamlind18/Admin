import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W / "split_c.png").as_uri()
css = f"""
body{{background:#ddd url('{BG}') center/cover no-repeat}}
.l{{position:absolute;top:58px;width:540px;text-align:center;color:#fff;font:500 56px/1 'EB Garamond';letter-spacing:.3px;
  text-shadow:0 2px 10px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.4)}}
.a{{left:0}} .b{{left:540px}}
"""
body = '<div class="l a">hennes tvättstuga</div><div class="l b">min</div>'
ADS = [{"out": "N5_hennes_min_1x1.png", "w": 1080, "h": 1080, "css": css, "body": body}]
