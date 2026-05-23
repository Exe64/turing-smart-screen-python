# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/
#
# Copyright (C) 2021 Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file allows to add custom data source as sensors and display them in System Monitor themes
# There is no limitation on how much custom data source classes can be added to this file
# See CustomDataExample theme for the theme implementation part

import json
import logging
import math
import os
import platform
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = Path(os.environ.get("CLAUDE_CREDENTIALS", Path.home() / ".claude" / ".credentials.json"))
USAGE_API_URL = "https://api.anthropic.com/api/oauth/usage"


class _ClaudeUsageCache:
    """Shared cache for Claude API usage data, refreshed at most every 30 seconds."""

    _data: Optional[dict] = None
    _last_fetch: float = 0
    _ttl: float = 30

    @classmethod
    def get(cls) -> Optional[dict]:
        now = time.time()
        if cls._data is not None and (now - cls._last_fetch) < cls._ttl:
            return cls._data
        try:
            with open(CREDENTIALS_PATH) as f:
                creds = json.load(f)
            token = creds["claudeAiOauth"]["accessToken"]
            resp = requests.get(
                USAGE_API_URL,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            resp.raise_for_status()
            cls._data = resp.json()
            cls._last_fetch = now
        except Exception as e:
            logger.warning("Failed to fetch Claude usage: %s", e)
            if cls._data is None:
                cls._data = {}
        return cls._data


# Custom data classes must be implemented in this file, inherit the CustomDataSource and implement its 2 methods
class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # If there is no numeric value, keep this function empty
        pass

    @abstractmethod
    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        # If you do not want to draw a line graph or if your custom data has no numeric values, keep this function empty
        pass


# Example for a custom data class that has numeric and text values
class ExampleCustomNumericData(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10  # By default, it is filed with math.nan values to indicate there is no data stored

    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # Here a Python function from another module can be called to get data
        # Example: self.value = my_module.get_rgb_led_brightness() / audio.system_volume() ...
        self.value = 75.845

        # Store the value to the history list that will be used for line graph
        self.last_val.append(self.value)
        # Also remove the oldest value from history list
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text.
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        # Example here: format numeric value: add unit as a suffix, and keep 1 digit decimal precision
        return f'{self.value:>5.1f}%'
        # Important note! If your numeric value can vary in size, be sure to display it with a default size.
        # E.g. if your value can range from 0 to 9999, you need to display it with at least 4 characters every time.
        # --> return f'{self.as_numeric():>4}%'
        # Otherwise, part of the previous value can stay displayed ("ghosting") after a refresh

    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        return self.last_val


# Example for a custom data class that only has text values
class ExampleCustomTextOnlyData(CustomDataSource):
    def as_numeric(self) -> float:
        # If there is no numeric value, keep this function empty
        pass

    def as_string(self) -> str:
        # If a custom data class only has text values, it won't be possible to display graph or radial bars
        return "Python: " + platform.python_version()

    def last_values(self) -> List[float]:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass


class ClaudeFiveHourUsage(CustomDataSource):
    last_val = [math.nan] * 20

    def as_numeric(self) -> float:
        data = _ClaudeUsageCache.get()
        self.value = 0.0
        self.resets_at = ""
        if data and "five_hour" in data and data["five_hour"]:
            self.value = float(data["five_hour"].get("utilization", 0) or 0)
            raw_reset = data["five_hour"].get("resets_at", "")
            if raw_reset:
                try:
                    dt = datetime.fromisoformat(raw_reset)
                    self.resets_at = dt.strftime("%H:%M")
                except Exception:
                    self.resets_at = ""
        self.last_val.append(self.value)
        self.last_val.pop(0)
        return self.value

    def as_string(self) -> str:
        return f'{self.value:>5.1f}%'

    def last_values(self) -> List[float]:
        return self.last_val


class ClaudeFiveHourReset(CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        data = _ClaudeUsageCache.get()
        if data and "five_hour" in data and data["five_hour"]:
            raw = data["five_hour"].get("resets_at", "")
            if raw:
                try:
                    dt = datetime.fromisoformat(raw)
                    return f'Reset {dt.strftime("%H:%M")}'
                except Exception:
                    pass
        return ""

    def last_values(self) -> List[float]:
        pass


class ClaudeWeeklyUsage(CustomDataSource):
    last_val = [math.nan] * 20

    def as_numeric(self) -> float:
        data = _ClaudeUsageCache.get()
        self.value = 0.0
        if data and "seven_day" in data and data["seven_day"]:
            self.value = float(data["seven_day"].get("utilization", 0) or 0)
        self.last_val.append(self.value)
        self.last_val.pop(0)
        return self.value

    def as_string(self) -> str:
        return f'{self.value:>5.1f}%'

    def last_values(self) -> List[float]:
        return self.last_val


class ClaudeWeeklyReset(CustomDataSource):
    def as_numeric(self) -> float:
        pass

    def as_string(self) -> str:
        data = _ClaudeUsageCache.get()
        if data and "seven_day" in data and data["seven_day"]:
            raw = data["seven_day"].get("resets_at", "")
            if raw:
                try:
                    dt = datetime.fromisoformat(raw)
                    return f'Reset {dt.strftime("%a %d")}'
                except Exception:
                    pass
        return ""

    def last_values(self) -> List[float]:
        pass


class ClaudeSonnetUsage(CustomDataSource):
    def as_numeric(self) -> float:
        data = _ClaudeUsageCache.get()
        self.value = 0.0
        if data and "seven_day_sonnet" in data and data["seven_day_sonnet"]:
            self.value = float(data["seven_day_sonnet"].get("utilization", 0) or 0)
        return self.value

    def as_string(self) -> str:
        return f'{self.value:>5.1f}%'

    def last_values(self) -> List[float]:
        pass


class ClaudeExtraUsage(CustomDataSource):
    def as_numeric(self) -> float:
        data = _ClaudeUsageCache.get()
        self.value = 0.0
        if data and "extra_usage" in data and data["extra_usage"]:
            self.value = float(data["extra_usage"].get("used_credits", 0) or 0)
        return self.value

    def as_string(self) -> str:
        return f'{self.value:>7.1f} EUR'

    def last_values(self) -> List[float]:
        pass
