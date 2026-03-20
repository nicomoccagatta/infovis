#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict
import csv
import argparse
from typing import Any, Dict, List


def find_files(root: Path, pattern: str) -> List[Path]:
    return sorted(root.glob(pattern))


def get_contributions_collection(obj: Dict[str, Any]) -> Dict[str, Any]:
    # handle top-level or nested GraphQL response
    if 'contributionsCollection' in obj:
        return obj['contributionsCollection']
    if isinstance(obj.get('data'), dict):
        user = obj['data'].get('user')
        if isinstance(user, dict) and 'contributionsCollection' in user:
            return user['contributionsCollection']
    return {}


def extract_day_counts(collection: Dict[str, Any]) -> Dict[str, int]:
    counts = {}
    calendar = collection.get('contributionCalendar') or {}
    weeks = calendar.get('weeks') or []
    for week in weeks:
        for day in week.get('contributionDays', []) or []:
            date = day.get('date')
            if not date:
                continue
            # common key is 'contributionCount'
            cnt = day.get('contributionCount')
            if cnt is None:
                # try other plausible keys
                cnt = day.get('count') or day.get('contributions') or 0
            counts[date] = counts.get(date, 0) + int(cnt)
    return counts


def aggregate_totals(collection: Dict[str, Any], totals_acc: Dict[str, int]):
    keys = [
        'totalCommitContributions',
        'totalIssueContributions',
        'totalPullRequestContributions',
        'totalPullRequestReviewContributions',
        'totalRepositoryContributions',
    ]
    for k in keys:
        val = collection.get(k)
        if isinstance(val, int):
            totals_acc[k] = totals_acc.get(k, 0) + val


def merge_files(files: List[Path]) -> Dict[str, Any]:
    per_date = defaultdict(int)
    totals: Dict[str, int] = {}
    accounts = []

    for fp in files:
        try:
            data = json.loads(fp.read_text())
        except Exception as e:
            print(f"Warning: failed to read {fp}: {e}")
            continue

        coll = get_contributions_collection(data)
        if not coll:
            print(f"Warning: no contributionsCollection in {fp}")
        day_counts = extract_day_counts(coll)
        for d, c in day_counts.items():
            per_date[d] += c

        aggregate_totals(coll, totals)

        # record account id if present
        account_label = data.get('login') or data.get('name') or fp.stem
        accounts.append(account_label)

    merged_dates = sorted(per_date.items())
    return {
        'accounts': accounts,
        'merged_dates': [{'date': d, 'count': c} for d, c in merged_dates],
        'totals': totals,
    }


def write_outputs(root: Path, merged: Dict[str, Any]):
    out_json = root / 'merged_stats.json'
    out_csv = root / 'merged_stats.csv'
    out_json.write_text(json.dumps(merged, indent=2, ensure_ascii=False))

    with out_csv.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'count'])
        for item in merged['merged_dates']:
            writer.writerow([item['date'], item['count']])

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_csv}")


def main():
    parser = argparse.ArgumentParser(description='Merge GitHub contribution JSONs')
    parser.add_argument('--dir', '-d', default=Path(__file__).parent, type=Path,
                        help='Directory with commits-*.json files')
    parser.add_argument('--pattern', '-p', default='commits-*.json')
    args = parser.parse_args()

    root = args.dir
    files = find_files(root, args.pattern)
    if not files:
        print(f'No files found in {root} matching {args.pattern}')
        return

    print(f'Found {len(files)} files, merging...')
    merged = merge_files(files)
    write_outputs(root, merged)
    print('Summary:')
    print(json.dumps({'accounts': merged['accounts'], 'total_days': len(merged['merged_dates'])}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
