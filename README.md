# Flowytravel Feed Pipeline

Deze repository beheert de feed-snapshots voor Flowytravel.

## Doel

GitHub haalt externe feeds op, bewaart snapshots, controleert data en maakt delta-bestanden. Base44 hoeft daardoor later minder zware imports te draaien.

## Structuur

```text
snapshots/
  tui/
    latest/
    previous/

audits/
  tui/

scripts/

configs/

.github/workflows/
