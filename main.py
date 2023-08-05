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

_LOG_FILE_NAME = 'plex_delete_events.log'
_RU_TORRENT_DATA_DIR_PATH = '/media/sdp1/fizz/private/rtorrent/data/'
_EXCLUDED_DIR_NAMES = {
    f'/{str.casefold(h)}/' for h in [
        # Add any folder names to exclude
        "Baldurs.Gate.3-RUNE",  # baldurs balls
    ]
}
_EXCLUDED_HASHES = {
    str.casefold(h) for h in [
        # Add any torrent hashes to exclude
        '645903B8BA5E7FF466BEAC3E6467BFF91B671CB8',  # baldurs balls  #  noqa
    ]
}
_EXCLUDED_FILENAMES = {
    str.casefold(fn) for fn in [
        # Add any filenames to exclude
        'Surveillance Camera Man Surveillance Camera Man 1-8 mP5ZVPwP7bg 22.mp4',  # noqa
    ]
}
_DAYS_SINCE_TOUCHED = int(os.getenv('DAYS_SINCE_TOUCHED', '30'))
_PLEX_URL = os.getenv('PLEX_URL')
_PLEX_TOKEN = os.getenv('PLEX_TOKEN')
_RU_TORRENT_RPC_URL = os.getenv('RU_TORRENT_RPC_URL')


def get_current_utc_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def log_and_print(message):
    print(message)
    with open(_LOG_FILE_NAME, 'a', encoding='utf-8') as f:
        f.write(f'[{get_current_utc_timestamp()} UTC] {message}\n')


def _get_unexpired_filenames(plex, amount_of_days_considered_expired):
    # we get all "items" from plex, this includes shows, movies, etc.
    items = [item for s in plex.library.sections() for item in s.all()]

    # for every item, we get the path of the file(s) associated with it
    # i.e "path/to/a.mkv", "path/to/b.mp4"
    unexpired_filenames = set()
    for i in items:
        filepaths = set()
        if isinstance(i, Show):
            filepaths |= {
                p.file for e in i.episodes() for m in e.media for p in m.parts
            }
        elif isinstance(i, Movie):
            filepaths |= {p.file for m in i.media for p in m.parts}

        # we only care about the filename, not the path, so we get the basename,
        # note that we case-fold the filename, as we don't care about case
        # i.e "a.mkv", "b.mp4"
        filenames = {str.casefold(os.path.basename(fp)) for fp in filepaths}

        # if the item has been watched, we get the last time it was watched
        # if there is no history, then we use the time it was added to plex
        last_watched = i.addedAt
        if history := i.history():
            latest_history = max(history, key=lambda h: h.viewedAt)
            last_watched = latest_history.viewedAt

        # if we somehow can't get the last time it was watched, then we skip it
        if not last_watched:
            log_and_print(f"Couldn't get last watched time for {i.title}")
            continue

        # we get the number of days since the item was last watched
        days_since_watched = (datetime.now() - last_watched).days

        # if the item was watched within the amount of days we consider
        # to be expired, then we add the filenames to the set of unexpired
        # filenames, so that we don't delete them later
        is_expired = days_since_watched >= amount_of_days_considered_expired
        if not is_expired:
            unexpired_filenames |= filenames

    # we return the set of filenames that are not expired
    return unexpired_filenames


# this function is used to get all the filepaths, given a base path
# i.e. if the base path is a directory, then we get all the files in that
# directory and all subdirectories, if the base path is a file, then we
# just get that file, if the base path is neither a file or directory,
# then we return an empty set
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
        raise ValueError('Missing an environment variable... check the script.')

    plex = PlexServer(_PLEX_URL, _PLEX_TOKEN)

    # we get all the filenames that are not expired
    unexpired_fileset = _get_unexpired_filenames(plex, _DAYS_SINCE_TOUCHED)
    unexpired_filepath_set = set()

    ru_torrent = xmlrpc.client.ServerProxy(_RU_TORRENT_RPC_URL)

    # we get all the torrents that are currently downloading/seeding
    torrent_hashes = set(ru_torrent.download_list('', 'main'))

    for torrent_hash in torrent_hashes:
        # we skip any torrents that we don't care about
        if str.casefold(torrent_hash) in _EXCLUDED_HASHES:
            continue

        # we get the name and base path of the torrent
        # i.e. "name", "path/to/torrent"
        torrent_name = ru_torrent.d.name(torrent_hash)
        torrent_base_path = ru_torrent.d.base_path(torrent_hash)

        # we skip any torrents that aren't in the data directory
        if not torrent_base_path.startswith(_RU_TORRENT_DATA_DIR_PATH):
            print(f"Check this torrent's path: {torrent_name}")
            continue

        # we get all the paths of the files associated with the torrent
        torrent_filepath_set = _filepath_set(torrent_base_path)
        if not torrent_filepath_set:
            print(f"Check this torrent's files: {torrent_name}")
            continue

        # we get all the filenames associated with the torrent
        torrent_fileset = {str.casefold(os.path.basename(f)) for f in torrent_filepath_set}

        # if the torrent has any files that are not expired, then we add them
        # to the set of unexpired filepaths, and we skip the torrent
        if torrent_fileset & unexpired_fileset:
            unexpired_filepath_set |= torrent_filepath_set
            continue

        # if all the files associated with the torrent are expired (because we didn't skip it)
        # then we remove the torrent and all its files
        with contextlib.suppress(Exception):
            if ru_torrent.d.erase(torrent_hash) == 0:
                if os.path.isfile(torrent_base_path):
                    os.remove(torrent_base_path)
                elif os.path.isdir(torrent_base_path):
                    shutil.rmtree(torrent_base_path)
                log_and_print(f'Removed torrent: {torrent_name}')

    # we go through all the files in the ruTorrent data directory
    # and remove any that are not in the unexpired fileset (because they're expired)
    ru_torrent_base_path = ru_torrent.directory.default()
    for root, _, files in os.walk(ru_torrent_base_path):
        for filename in files:
            # if we want to keep any files (i.e. surveillance camera man) we skip them
            if str.casefold(filename) in _EXCLUDED_FILENAMES:
                continue

            # we skip any files that haven't expired yet
            if filename in unexpired_fileset:
                continue

            # we skip any full paths to files that haven't expired yet
            filepath = os.path.join(root, filename)
            if filepath in unexpired_filepath_set:
                continue

            # skip any where we exclude the folder specifically
            if any(d in filepath for d in _EXCLUDED_DIR_NAMES):
                continue

            # we remove the file, as it has expired
            os.remove(filepath)

            # we log the removal so we know what was removed
            log_and_print(f'Removed by clean-up ({_DAYS_SINCE_TOUCHED} days since last watched): {filename}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
