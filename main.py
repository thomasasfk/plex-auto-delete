from __future__ import annotations

import argparse
from datetime import datetime
from typing import Sequence

from plexapi.server import PlexServer


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Delete old media files from a Plex server',
    )
    parser.add_argument(
        '--url',
        required=True,
        help='URL of the Plex server',
    )
    parser.add_argument(
        '--token',
        required=True,
        help='Access token for the Plex server',
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days after which files should be deleted',
    )
    args = parser.parse_args(argv)

    plex = PlexServer(args.url, args.token)
    items = [
        item for section in plex.library.sections() for item in section.all()
    ]
    for item in items:
        history = item.history()
        last_watched = history[0].viewedAt if history else item.addedAt
        if not last_watched:
            continue

        days_since_watched = (datetime.now() - last_watched).days
        if days_since_watched >= args.days:
            # deleting will remove the file but not the torrent in ruTorrent
            # we need to query the ruTorrent API and match something,
            # then delete the torrent and the data with it.
            item.delete()
            print(f'Deleted {item.title} ({item.year})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
