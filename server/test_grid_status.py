"""Regression checks for the deployed grid-to-port layout."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch

import grid_status_api


class GridStatusTest(unittest.TestCase):
    def test_status_uses_original_grid_port_order(self):
        """Keep all status labels aligned with deployed ports and custom bases."""
        layout = [
            "A1", "B1", "C1", "D1", "E1",
            "A2", "B2", "C2", "D2", "E2",
            "A3", "B3", "C3", "D3", "E3",
            "A4", "B4", "C4", "D4", "E4",
            "A5", "B5", "C5", "D5", "E5",
        ]
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.json"
            for base_port in (35710, 40000):
                with self.subTest(base_port=base_port):
                    config_path.write_text(json.dumps({
                        "server_ip": "192.0.2.1",
                        "rcon_port_start": base_port,
                    }), encoding="utf-8")
                    with patch.object(grid_status_api, "CONFIG_PATH", config_path), patch.object(
                        grid_status_api, "is_port_open",
                        side_effect=lambda host, port: port == base_port + 1,
                    ) as probe:
                        response = grid_status_api.app.test_client().get("/api/grid-status")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(set(response.json), set(layout))
                    self.assertEqual(probe.call_args_list, [
                        call("192.0.2.1", base_port + index) for index in range(25)
                    ])
                    for grid in layout:
                        self.assertEqual(
                            response.json[grid]["status"],
                            "online" if grid == "B1" else "offline",
                            grid,
                        )
