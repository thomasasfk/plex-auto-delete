import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

from main import main


@patch('main.PlexServer')
def test_main(mock_plex_server):
    mock_item1 = MagicMock()
    mock_item1.title = 'Item 1'
    mock_item1.year = 2020
    mock_item1.addedAt = datetime.datetime(2022, 1, 1)
    mock_item1.history.return_value = []

    mock_item2 = MagicMock()
    mock_item2.title = 'Item 2'
    mock_item2.year = 2021
    mock_item2.addedAt = datetime.datetime(2022, 1, 1)
    mock_item2.history.return_value = [
        MagicMock(viewedAt=datetime.datetime(2022, 1, 1)),
    ]

    mock_section = MagicMock()
    mock_section.all.return_value = [mock_item1, mock_item2]

    mock_library = MagicMock()
    mock_library.sections.return_value = [mock_section]

    mock_plex_server.return_value = MagicMock(library=mock_library)

    with patch('builtins.print') as mock_print:
        assert main([
            '--url',
            'http://localhost:32400',
            '--token',
            'abcd1234',
            '--days',
            '30',
        ]) == 0

    assert mock_plex_server.call_args == (
        ('http://localhost:32400', 'abcd1234'),
    )
    assert mock_section.all.call_count == 1
    assert mock_item1.history.call_count == 1
    assert mock_item2.history.call_count == 1

    expected_calls = [
        (('Deleted Item 1 (2020)',), {}),
        (('Deleted Item 2 (2021)',), {}),
    ]
    assert [tuple(c) for c in mock_print.call_args_list] == expected_calls
    assert mock_item1.delete.call_count == 1
    assert mock_item2.delete.call_count == 1
