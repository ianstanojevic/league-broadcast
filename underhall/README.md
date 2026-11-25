# Underhåll av Arenan-stilen

Den här mappen behövs **inte** för att använda stilen – bara för att ändra den.
För att använda den: se [README:n i roten](../README.md).

| Var | Vad som är stylat |
|---|---|
| Champ select (`/pregame/v2`) | Pick & ban-raden, bronsramar, turneringsloggan i mitten |
| Under matchen (`/ingame/v2`) | Scoreboard, champion-flikar, färger och typsnitt på alla element |
| Post-game | – (kräver League Broadcast Basic, ingår inte) |

## Mappar

```
Arenan_pre.lbstyle, Arenan_in.lbstyle   (i roten) exporterade stilset – det man importerar
bilder/                                 (i roten) bilderna i README:n
underhall/arenan/style/   vår design som rå JSON (samma som i .lbstyle-filerna)
underhall/arenan/logo/    gladiator.png (turneringsloggan) + ett eget emblem som alternativ
underhall/tools/          skript för att underhålla stilen
underhall/raw/            råa skärmdumpar (inte i git)
```

## Verktyg

Kör från repots rot. Kräver Python 3 (+ Pillow för bilderna) och Node 22+.

| Skript | Gör |
|---|---|
| `python underhall/tools/apply_arenan.py` | Lägger på stilen i League Broadcasts filer igen. **Stäng appen först.** Kräver att stilseten "Arenan" redan finns (importerade eller duplicerade). `--dry-run` visar bara vad som skulle ändras. |
| `python underhall/tools/outline.py <variant.json>` | Visar hur ett stilelement är uppbyggt (noder, färger, typsnitt). |
| `python underhall/tools/make_logo.py` | Ritar om emblemet i `underhall/arenan/logo/`. |
| `node underhall/tools/capture.mjs <url> <ut.png> [sek] [selector] [antal]` | Skärmdump av en overlay i 1920×1080 (headless Edge). League Broadcast måste köra mock-data. |
| `python underhall/tools/make_screenshots.py` | Gör bilderna i `bilder/` av råbilderna i `underhall/raw/`. |
| `python underhall/tools/make_banner.py` | Gör bannern `underhall/arenan/logo/banner.png` (1280×640). Den används bara som länkförhandsvisning – ladda upp den under Settings → Social preview. |

Nya `.lbstyle`-filer efter en ändring: i League Broadcast, Style Editor → klicka på stilsetets namn → Export,
eller `GET http://localhost:58869/api/style/set/<pre|in>/Arenan/export`.

## Bra att veta om League Broadcast

- Stilarna ligger i `%APPDATA%\BlueBottle\LeagueBroadcast\data\style\`. Filer under `preset/` skrivs över varje gång appen startar – ändra bara egna kopior (Duplicate style set / Duplicate variant).
- `customCss` på ett element läggs in som en stilmall för hela sidan, så ett `:root { --lb-overlay-… }`-block färgar om alla element.
- Typsnitt som anges i `fontFamily` hämtar appen själv från Google Fonts.
- Turneringsloggan gäller hela säsongen (Style Editor → Global Styles → Tournament Icon), inte ett enskilt stilset.
- Bara `/ingame/v2` och `/pregame/v2` använder stilen; `/ingame/` är den gamla layouten.

## Begränsningar

- Testat med League Broadcasts mock-data, inte i en riktig spectatad match än.
- Importen av `.lbstyle` är inte testad på en annan dator.
- `gladiator.png` är en meme med en filmbild och lagloggor som andra äger – okej för en privat stream med kompisar,
  men använd emblemet i `arenan/logo/` om ni streamar publikt.

League Broadcast är en produkt från BlueBottle GmbH; det här repot är inte kopplat till dem eller till Riot Games.
