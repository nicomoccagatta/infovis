import json
from pathlib import Path

INPUT = Path(__file__).parent / "commits_spotify_merged_data_with_genres.json"

data = json.loads(INPUT.read_text(encoding="utf-8"))

for entry in data:
    if "artist_msPlayed" in entry:
        ms = entry.pop("artist_msPlayed")
        entry["artist_minutesPlayed"] = round(ms / 60_000, 2)

INPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Convertidos {len(data)} registros: artist_msPlayed → artist_minutesPlayed (minutos)")
