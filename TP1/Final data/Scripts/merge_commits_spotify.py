import json
from datetime import datetime
from collections import defaultdict

# Load commits data
with open('commits-history/merged_stats.json', 'r') as f:
    commits_data = json.load(f)

# Create a dictionary with commits by date
commits_by_date = {}
for entry in commits_data['merged_dates']:
    commits_by_date[entry['date']] = entry['count']

# Load and process Spotify music data
spotify_by_date = defaultdict(lambda: defaultdict(int))  # {date: {artist: total_msPlayed}}

music_files = [
    'TP1/Final data/StreamingHistory_music_0.json',
    'TP1/Final data/StreamingHistory_music_1.json',
    'TP1/Final data/StreamingHistory_music_2.json',
    'TP1/Final data/StreamingHistory_music_3.json',
    'TP1/Final data/StreamingHistory_music_4.json',
]

for file_path in music_files:
    with open(file_path, 'r') as f:
        music_data = json.load(f)
        for track in music_data:
            # Extract date from endTime (format: "2025-03-14 04:15")
            date_str = track['endTime'][:10]  # "2025-03-14"
            artist = track['artistName']
            ms_played = track['msPlayed']
            
            spotify_by_date[date_str][artist] += ms_played

# Create final merged data
final_data = []

# Get all unique dates
all_dates = set(commits_by_date.keys()) | set(spotify_by_date.keys())
all_dates = sorted(list(all_dates))

for date in all_dates:
    # Get commits count for this date
    commits_count = commits_by_date.get(date, 0)
    
    # Get top artist for this date
    artists_on_date = spotify_by_date.get(date, {})
    
    if artists_on_date:
        # Find the artist with max total msPlayed
        top_artist = max(artists_on_date, key=artists_on_date.get)
        top_artist_ms = artists_on_date[top_artist]
        
        final_data.append({
            "date": date,
            "commits": commits_count,
            "top_artist": top_artist,
            "artist_msPlayed": top_artist_ms
        })
    else:
        final_data.append({
            "date": date,
            "commits": commits_count,
            "top_artist": None,
            "artist_msPlayed": 0
        })

# Save final merged data
with open('TP1/Final data/merged_commits_spotify.json', 'w') as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"✓ Merged data saved to TP1/Final data/merged_commits_spotify.json")
print(f"✓ Total days: {len(final_data)}")
print(f"\nFirst 10 entries:")
for entry in final_data[:10]:
    print(json.dumps(entry, ensure_ascii=False))
