import argparse
import json
from pathlib import Path


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_artist_map_from_input(data, artist_key: str):
    artists = set()
    for entry in data:
        artist = entry.get(artist_key)
        if isinstance(artist, str) and artist.strip():
            artists.add(artist.strip())
    # Valor placeholder: lo vas completando manualmente.
    return {artist: "Por definir" for artist in sorted(artists)}


def main():
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Agrega 'genero_musical' a cada elemento usando un mapeo editable por artista."
    )
    parser.add_argument(
        "--input",
        default=str(base_dir / "commits_spotify_merged_data.json"),
        help="Ruta al JSON de entrada.",
    )
    parser.add_argument(
        "--output",
        default=str(base_dir / "commits_spotify_merged_data_with_genres.json"),
        help="Ruta al JSON de salida.",
    )
    parser.add_argument(
        "--mapping",
        default=str(base_dir / "artist_genres.json"),
        help="Ruta al JSON con el mapeo { artista: genero }.",
    )
    parser.add_argument(
        "--artist-key",
        default="top_artist",
        help="Nombre de la clave del artista en cada elemento.",
    )
    parser.add_argument(
        "--genre-key",
        default="genero_musical",
        help="Nombre de la clave a agregar en cada elemento.",
    )
    parser.add_argument(
        "--init-map",
        action="store_true",
        help="Inicializa (o re-crea) el archivo de mapeo con los artistas del input.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    mapping_path = Path(args.mapping)

    data = load_json(input_path, default=None)
    if data is None:
        raise FileNotFoundError(f"No se encontró el input: {input_path}")
    if not isinstance(data, list):
        raise ValueError("El JSON de entrada debe ser una lista de objetos.")

    if args.init_map:
        artist_map = build_artist_map_from_input(data, args.artist_key)
        save_json(mapping_path, artist_map)
        print(f"✓ Mapa de artistas creado: {mapping_path}")
        print(f"  Artistas encontrados: {len(artist_map)}")
        return

    artist_map = load_json(mapping_path, default=None)
    if not isinstance(artist_map, dict):
        artist_map = {}

    # Agregamos cualquier artista nuevo al mapping con placeholder.
    auto_added = []
    for entry in data:
        artist = entry.get(args.artist_key)
        if isinstance(artist, str):
            artist = artist.strip()
        else:
            continue
        if artist and artist not in artist_map:
            artist_map[artist] = "Por definir"
            auto_added.append(artist)

    if auto_added:
        save_json(mapping_path, artist_map)
        print(f"⚠️ Se agregaron {len(auto_added)} artistas nuevos al mapeo ({mapping_path}).")

    missing = set()
    for entry in data:
        artist = entry.get(args.artist_key)
        if isinstance(artist, str):
            artist = artist.strip()
        else:
            artist = None

        if not artist:
            entry[args.genre_key] = "Por definir"
            continue

        genre = artist_map.get(artist, "Por definir")
        entry[args.genre_key] = genre
        if genre == "Por definir":
            missing.add(artist)

    save_json(output_path, data)
    print(f"✓ Salida guardada: {output_path}")
    print(f"  Artistas sin género definido: {len(missing)}")


if __name__ == "__main__":
    main()

