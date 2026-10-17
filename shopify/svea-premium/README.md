# Svea Premium – sektioner och mallar för sveaskincare.se

Säkerhetskopia av det som byggdes i arbetskopian **"SVEA SKIN 4 – Premium (arbetskopia)"**
(`gid://shopify/OnlineStoreTheme/209822613842`, opublicerad) i oktober 2026. Live-temat är inte ändrat.

## Innehåll

| Mapp | Vad |
|---|---|
| `sections/svp-*.liquid` | 18 premiumsektioner ("Svea Premium – …" i temaredigeraren) |
| `snippets/svp-*.liquid` | Bild/platshållare och ikoner som sektionerna använder |
| `assets/svp-base.css` | Gemensamt designsystem (typsnitt, färger, knappar, skydd mot temats globala regler) |
| `templates/product.pdrn-a-mekanism.json` | Produktsida A "Mekanismen" (`?view=pdrn-a-mekanism`) |
| `templates/product.pdrn-b-spegel.json` | Produktsida B "Spegelmomentet" (`?view=pdrn-b-spegel`) |
| `templates/index.json` | Ny startsida |
| `sections/header-group.json`, `footer-group.json` | Lugn annonsrad, meny i sidhuvudet, "stift" i sidfoten |

Ändringar i temats egna filer (inte kopierade hit, eftersom Elixir är ett licensierat tema):
- `sections/header.liquid`: logotypen är inte längre en `<h1>` på startsidan.
- `locales/sv.json`: "Log in" → "Logga in".

`svp-design` ska alltid ligga först i en mall som använder svp-sektioner. Den laddar typsnitt
(Newsreader och Bricolage Grotesque från Shopifys typsnittsbibliotek), färger och `svp-base.css`.

## Återställa

Ladda upp filerna till ett tema med samma sökvägar (Shopify admin › Teman › Redigera kod, eller
Admin API `themeFilesUpsert`). Mallarna förutsätter Kaching Bundles-appen (appblock i `svp-pdp-main`).
