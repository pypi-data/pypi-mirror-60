
import pytest

from .amdcovc import _parse_amdcovc_status, AMDCOVC

text = """
Adapter 0: Vega 10 XL/XT [Radeon RX Vega 56/64]
  Device Topology: 47:0:0
  Vendor ID: 4098 (0x1002)
  Device ID: 26751 (0x687f)
  Current CoreClock: 852 MHz
  Current MemoryClock: 800 MHz
  Core Overdrive: 0
  Memory Overdrive: 0
  Performance Control: auto
  GPU Load: 0%
  Current BusSpeed: 0
  Current BusLanes: 0
  Temperature: 25 C
  Temperature2: 25 C
  Temperature3: 23 C
  Critical temperature: 85 C
  FanSpeed Min (Value): 0
  FanSpeed Max (Value): 255
  Current FanSpeed: 25.000%
  Controlled FanSpeed: no
  Core Clocks:
    852MHz
    991MHz
    1138MHz
    1269MHz
    1312MHz
    1474MHz
    1569MHz
    1622MHz
  Memory Clocks:
    167MHz
    500MHz
    700MHz
    800MHz
"""

class AMDCOVCModified(AMDCOVC):
    _TEST_fanspeed = None

    def popen_amdcovc(self, args):
        raise NotImplemented()

    def amdcovc_check_output(self, args):
        if args == ("-v",):
            return text.encode('utf8')

        if len(args) == 3 and args[:2] == ("-a", "0"):
            before, sep, after = args[2].partition("=")
            if before == "fanspeed" and sep:
                self._TEST_fanspeed = after
            return b''

        raise NotImplementedError()

def test_api():
    amd = AMDCOVCModified()
    adapters = amd.adapters
    assert len(adapters) == 1

    (key, adapter), = adapters.items()

    assert key == "47:0:0"

    assert adapter.fan_speed_is_firmware_controlled == False

    assert adapter.fan_speed == 0.25

    adapter.fan_speed = 0.50

    assert amd._TEST_fanspeed == "50"

    adapter.fan_speed = "default"

    assert amd._TEST_fanspeed == "default"

    with pytest.raises(TypeError):
        adapter.fan_speed = "boop"


