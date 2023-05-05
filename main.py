from __future__ import annotations

import contextlib
import os
import shutil
import xmlrpc.client
from datetime import datetime

from dotenv import load_dotenv  # noqa
from plexapi.server import PlexServer
from plexapi.video import Movie
from plexapi.video import Show
load_dotenv()

_RU_TORRENT_DATA_DIR_PATH = '/media/sdp1/fizz/private/rtorrent/data/'
_EXCLUDED_HASHES = {
    str.casefold(h) for h in [
        # Add any torrent hashes to exclude
    ]
}
_EXCLUDED_FILENAMES = {
    str.casefold(fn) for fn in [
        # Add any filenames to exclude
        'Surveillance Camera Man Surveillance Camera Man 1-8 mP5ZVPwP7bg 22.mp4', # noqa
    ]
}
_DAYS_SINCE_TOUCHED = int(os.getenv('DAYS_SINCE_TOUCHED', '30'))
_PLEX_URL = os.getenv('PLEX_URL')
_PLEX_TOKEN = os.getenv('PLEX_TOKEN')
_RU_TORRENT_RPC_URL = os.getenv('RU_TORRENT_RPC_URL')


def _get_unexpired_filenames(plex, days):
    items = [item for s in plex.library.sections() for item in s.all()]

    unexpired_filenames = set()
    for i in items:
        filepaths = set()
        if isinstance(i, Show):
            filepaths |= {
                p.file for e in i.episodes() for m in e.media for p in m.parts
            }
        elif isinstance(i, Movie):
            filepaths |= {p.file for m in i.media for p in m.parts}
        filenames = {str.casefold(os.path.basename(fp)) for fp in filepaths}

        last_watched = i.addedAt
        if history := i.history():
            latest_history = max(history, key=lambda h: h.viewedAt)
            last_watched = latest_history.viewedAt

        if not last_watched:
            continue

        days_since_watched = (datetime.now() - last_watched).days
        is_expired = days_since_watched >= days
        if not is_expired:
            unexpired_filenames |= filenames

    return unexpired_filenames


def _filepath_set(base_path):
    if os.path.isdir(base_path):
        filepaths = set()
        for root, _, files in os.walk(base_path):
            filepaths |= {os.path.join(root, f) for f in files}
        return filepaths
    elif os.path.isfile(base_path):
        return {base_path}
    return set()


def main() -> int:
    if not all([_PLEX_URL, _PLEX_TOKEN, _RU_TORRENT_RPC_URL]):
        raise ValueError('Missing environment variable... check the script.')

    plex = PlexServer(_PLEX_URL, _PLEX_TOKEN)
    unexpired_fileset = _get_unexpired_filenames(plex, _DAYS_SINCE_TOUCHED)
    unexpired_filepath_set = set()

    ru_torrent = xmlrpc.client.ServerProxy(_RU_TORRENT_RPC_URL)
    torrent_hashes = set(ru_torrent.download_list('', 'main'))
    for torrent_hash in torrent_hashes:
        torrent_name = ru_torrent.d.name(torrent_hash)
        if str.casefold(torrent_hash) in _EXCLUDED_HASHES:
            continue

        torrent_base_path = ru_torrent.d.base_path(torrent_hash)
        if not torrent_base_path.startswith(_RU_TORRENT_DATA_DIR_PATH):
            print(f"Check this torrent's path: {torrent_name}")
            continue

        torrent_filepath_set = _filepath_set(torrent_base_path)
        if not torrent_filepath_set:
            print(f"Check this torrent's files: {torrent_name}")
            continue

        torrent_fileset = {
            str.casefold(os.path.basename(f)) for f in torrent_filepath_set
        }
        if torrent_fileset & unexpired_fileset:
            unexpired_filepath_set |= torrent_filepath_set
            continue

        with contextlib.suppress(Exception):
            if ru_torrent.d.erase(torrent_hash) == 0:
                if os.path.isfile(torrent_base_path):
                    os.remove(torrent_base_path)
                elif os.path.isdir(torrent_base_path):
                    shutil.rmtree(torrent_base_path)
                print(f'Removed torrent: {torrent_name}')

    ru_torrent_base_path = ru_torrent.directory.default()
    for root, _, files in os.walk(ru_torrent_base_path):
        for filename in files:
            if str.casefold(filename) in _EXCLUDED_FILENAMES:
                continue

            if filename in unexpired_fileset:
                continue

            filepath = os.path.join(root, filename)
            if filepath in unexpired_filepath_set:
                continue

            os.remove(filepath)
            print(f'Removed by clean-up: {filename}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
