# Arenan – stilen för våra customkvällar i League Broadcast

Den här mappen innehåller allt för att få samma utseende som vi har:
mörkblått, brons och guld, Cinzel-typsnitt och gladiatorloggan.

| Fil | Vad det är |
|---|---|
| `Arenan_pre.lbstyle` | Champ select (pick & ban-raden längst ner), inklusive loggan |
| `Arenan_in.lbstyle` | Under matchen: scoreboard och champion-flikar, inklusive loggan |

## Installera

1. Installera **League Broadcast** (gratis) från <https://leaguebroadcast.gg/download> och logga in.
2. Öppna **Style Editor** i menyn till vänster.
3. Välj fliken **Pre** högst upp i listan.
   Klicka på stilsetets namn längst upp (det står **BottomRow**) → **Import Style Set** → välj `Arenan_pre.lbstyle`.
4. Välj fliken **In**.
   Klicka på stilsetets namn (**DefaultIngame**) → **Import Style Set** → välj `Arenan_in.lbstyle`.
5. Se till att **Arenan** är valt på båda flikarna (stilsetets namn högst upp ska vara *Arenan*).
   Om inte: klicka på namnet och välj Arenan i listan.

## OBS

Lägg till två **Browser**-källor, 1920 × 1080:

- Champ select: `http://localhost:58869/pregame/v2`
- Under matchen: `http://localhost:58869/ingame/v2`

**Glöm inte `/v2`** – utan det visar League Broadcast sin gamla layout och stilen syns inte.
League Broadcast måste vara igång när du streamar.

## Bra att veta

- Typsnitten (Cinzel och Barlow Condensed) hämtar League Broadcast själv första gången – datorn behöver internet.
- Post-game-grafiken ingår inte i gratisversionen av League Broadcast, så den har vi inte.
- Bara den som kör OBS och spectatar matchen behöver det här. Den som bara castar och pratar behöver inget installerat.
