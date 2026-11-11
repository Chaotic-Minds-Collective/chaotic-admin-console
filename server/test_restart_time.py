"""Regression checks for restart schedule timestamp validation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import grid_status_api


class RestartTimeTest(unittest.TestCase):
    def test_timestamps_require_an_offset(self):
        """Reject naive dates while preserving explicit UTC and nonzero offsets."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'restart.json'
            with patch.object(grid_status_api, 'RESTART_PATH', path):
                client = grid_status_api.app.test_client()
                self.assertEqual(client.get('/api/restart-time').status_code, 404)
                for value, status in [
                    ('2030-01-01T00:00:00', 500),
                    ('2030-01-01', 500),
                    ('invalid', 500),
                    ('2030-01-01T00:00:00Z', 200),
                    ('2030-01-01T00:00:00+00:00', 200),
                    ('2030-01-01T00:00:00+05:30', 200),
                ]:
                    with self.subTest(value=value):
                        path.write_text(json.dumps({'restart_time_utc': value}))
                        response = client.get('/api/restart-time')
                        self.assertEqual(response.status_code, status)
                        if status == 200:
                            self.assertEqual(response.json['restart_time_utc'], value)
