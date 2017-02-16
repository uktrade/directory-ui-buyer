from unittest.mock import patch

from company.templatetags import company_tags


@patch('company.helpers.chunk_list')
def test_external_url_handles_known_urls(mock_chunk_list):
    unchunked = [1, 2, 3, 4, 5]
    company_tags.chunk_list(unchunked, 3)

    mock_chunk_list.assert_called_once_with(unchunked, 3)
