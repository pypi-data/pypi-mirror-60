import requests
import json
from collections import namedtuple
from datetime import date, datetime, timedelta
from operator import attrgetter
import re
import pytz

US_FORMAT = "%m/%d/%Y %H:%M:%S"
ISO_FORMAT_UTC = "%Y-%m-%dT%H:%M:%SZ"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
REQUEST_FORMAT = "%Y-%m-%d"
UNIT_FORMATTER = re.compile(r"w")
UTC = pytz.utc


class MeterPeriodReading(object):
    def __init__(self, period_start, period_end, period_position, reading, unit="kWh"):
        self.period_start = datetime.strptime(period_start, ISO_FORMAT_UTC)
        self.period_start = UTC.localize(self.period_start)
        self.period_end = datetime.strptime(period_end, ISO_FORMAT_UTC)
        self.period_end = UTC.localize(self.period_end)
        self.period_position = int(period_position)
        self.reading = float(reading)
        if unit.isupper():
            unit = UNIT_FORMATTER.sub(r"W", unit.lower())
        self.unit = unit

    def to_json(self):
        return {
            "period_start": self.period_start.astimezone().strftime(ISO_FORMAT),
            "period_end": self.period_end.astimezone().strftime(ISO_FORMAT),
            "period_position": self.period_position,
            "reading": self.reading,
            "unit": self.unit,
        }

    def __repr__(self):
        return json.dumps(self.to_json(), indent=4)


class MeterReading(object):
    def __init__(self, date, reading, unit="kWh"):
        self.date = datetime.strptime(date, US_FORMAT)
        self.date = UTC.localize(self.date)
        self.reading = float(reading)
        if unit.isupper():
            unit = UNIT_FORMATTER.sub(r"W", unit.lower())
        self.unit = unit

    def to_json(self):
        return {
            "date": self.date.astimezone().strftime(ISO_FORMAT),
            "reading": self.reading,
            "unit": self.unit,
        }

    def __repr__(self):
        return json.dumps(self.to_json(), indent=4)


class ElOverblik(object):
    def __init__(self, refresh_token, metering_point):
        self._base_url = "https://api.eloverblik.dk/CustomerApi"
        self._refresh_token = refresh_token
        self._token = None
        self.metering_point = metering_point
        self.aggregations_types = ["Actual", "Quarter", "Hour", "Day", "Month", "Year"]
        self._auth()

    def _auth(self):
        url = f"{self._base_url}/api/token"
        headers = {"Authorization": f"Bearer {self._refresh_token}"}
        r = requests.get(url, headers=headers)
        if not r.ok:
            r.raise_for_status()
        self._token = r.json()["result"]

    def get_meter_readings(self, date_start, date_end):
        if isinstance(date_start, (date, datetime)):
            date_start = date_start.strftime(REQUEST_FORMAT)
        if isinstance(date_end, (date, datetime)):
            date_end = date_end.strftime(REQUEST_FORMAT)

        url = f"{self._base_url}/api/MeterData/GetMeterReadings/{date_start}/{date_end}"
        headers = {"Authorization": f"Bearer {self._token}"}
        body = {"meteringPoints": {"meteringPoint": [self.metering_point]}}
        r = requests.post(url, headers=headers, json=body)

        if not r.ok:
            if r.status_code == 401:
                self._auth()
                return self.get_meter_readings(date_start, date_end)
            r.raise_for_status()

        _json = r.json()["result"][0]["result"]["readings"]

        data = [
            MeterReading(x["readingDate"], x["meterReading"], x["measurementUnit"])
            for x in _json
        ]
        data.sort(key=attrgetter("date"), reverse=True)

        return data

    def get_meter_time_series(self, date_start, date_end, aggregation):
        aggregation = aggregation.title()

        if aggregation not in self.aggregations_types:
            raise ValueError(
                f"Aggregations is not allowed, allowed aggregations are: {str(allowed_aggregations)}"
            )

        if isinstance(date_start, (date, datetime)):
            date_start = date_start.strftime(REQUEST_FORMAT)
        if isinstance(date_end, (date, datetime)):
            date_end = date_end.strftime(REQUEST_FORMAT)

        url = f"{self._base_url}/api/MeterData/GetTimeSeries/{date_start}/{date_end}/{aggregation}"
        headers = {"Authorization": f"Bearer {self._token}"}
        body = {"meteringPoints": {"meteringPoint": [self.metering_point]}}
        r = requests.post(url, headers=headers, json=body)
        if not r.ok:
            if r.status_code == 401:
                self._auth()
                return self.get_meter_time_series(date_start, date_end, aggregation)
            r.raise_for_status()

        data = []
        _json = r.json()["result"][0]["MyEnergyData_MarketDocument"]["TimeSeries"]
        for series in _json:
            unit = series["measurement_Unit.name"]
            for period in series["Period"]:
                start = period["timeInterval"]["start"]
                end = period["timeInterval"]["end"]
                data += [
                    MeterPeriodReading(
                        start, end, x["position"], x["out_Quantity.quantity"], unit
                    )
                    for x in period["Point"]
                ]

        return data
