import re
import os
import subprocess
import sys

class AMDCOVC():
    def __init__(
        self,
        amdcovc_command: tuple = ("amdcovc",),
    ):
        self.amdcovc_command = amdcovc_command

        env = os.environ.copy()
        env.update(dict(
            AMDCOVC_NOCOLOR="y",
            AMDCOVC_NOBOLD="y",
        ))
        self.amdcovc_environ = env

    def popen_amdcovc(self, args: tuple) -> str:
        return subprocess.Popen(
            self.amdcovc_command + tuple(args),
            env=self.amdcovc_environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def amdcovc_check_output(self, args):
        """Same arguments as ``popen_amdcovc``."""
        proc = self.popen_amdcovc(args)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("amdcovc exited with nonzero status code")
        return stdout

    def update(self):
        status = self.amdcovc_check_output(("-v",)).decode(
            "utf8", errors="replace"
        )
        self.status = _parse_amdcovc_status(status)

    @property
    def adapters(self):
        self.update()
        return {k: Adapter(key=k, amdcovc=self) for k in self.status.keys()}

def _parse_amdcovc_status(text: str) -> dict:
    adapters = {}
    adapter = None
    last_property_key = None
    for line in text.split("\n"):
        if not line:
            continue
        m = _parse_re.match(line)
        if not m:
            raise ValueError("could not parse line {!r}".format(line))

        g = m.groupdict()
        if g["adapter_index"]:
            adapter_id = int(g["adapter_index"])
            adapters[adapter_id] = adapter = {}
            adapter["@adapter_index"] = adapter_id
            if g["adapter_name"]:
                adapter["@name"] = g["adapter_name"]
        elif g["property_key"]:
            last_property_key = g["property_key"]
            adapter[last_property_key] = g["property_value"]
        elif g["property_value_list_entry"]:
            last_prop = adapter[last_property_key]
            if not last_prop:
                adapter[last_property_key] = [
                    g["property_value_list_entry"]]
            elif isinstance(last_prop, list):
                adapter[last_property_key].append(
                    g["property_value_list_entry"])
            else:
                raise ValueError(
                    "property value list parse error, {!r}"
                    .format(text)
                )

    adapters_out = {}
    for adapter in adapters.values():
        key = adapter["Device Topology"]
        if key in adapters_out:
            raise RuntimeError(
                "two devices with identical device topology {!r}".format(key)
            )
        adapters_out[key] = adapter

    return adapters_out


_yes_no_dict = {"yes": True, "no": False}

class Adapter():
    key = None
    amdcovc = None

    def __init__(self, key: str, amdcovc: AMDCOVC):
        self.key = key
        self.amdcovc = amdcovc

    @property
    def status(self) -> dict:
        return self.amdcovc.status[self.key]

    def update(self):
        self.amdcovc.update()

    def _amdcovc_check_output(self, args: tuple):
        self.amdcovc.update()
        self.amdcovc.amdcovc_check_output((
            "-a",
            str(self.status["@adapter_index"]),
        ) + args)

    @property
    def fan_speed(self) -> float:
        """Fanspeed, as a floating point number between 0 and 1."""
        speed = self.status["Current FanSpeed"]
        assert speed[-1] == "%"
        return float(speed[:-1]) / 100.0

    @fan_speed.setter
    def fan_speed(self, value):
        if value == "default": # disable manual fan control
            pass
        elif isinstance(value, (float, int)):
            value = max(min(value, 1.0), 0.0)
            value = "{:.10g}".format(value * 100)
        else:
            raise TypeError("invalid fan speed {!r}".format(value))
        self._amdcovc_check_output(("fanspeed=" + value,))

    @property
    def fan_speed_is_firmware_controlled(self) -> bool:
        """
        Whether the fan speed is manually set by software rather than
        by the card's own firmware.

        To re-enable firmware control of the fan speed, do::

            adapter.fan_speed = "default"
        """
        return _yes_no_dict[self.status["Controlled FanSpeed"]]

    @property
    def temperature(self) -> float:
        return max(self.temperatures.values())

    @property
    def temperatures(self):
        """Temperatures in degrees Celsius."""
        result = {}
        for key, value in self.status.items():
            if key.startswith("Temperature"):
                assert value.endswith(" C")
                result[key] = float(value[:-2])
        return result

_parse_re = re.compile(
    r"(?:^Adapter (?P<adapter_index>\d+):(?: (?P<adapter_name>.*))?)|"
    r"(?:^  (?P<property_key>\S.*?):(?: (?P<property_value>.*))?)|"
    r"(?:^    (?P<property_value_list_entry>))"
)
