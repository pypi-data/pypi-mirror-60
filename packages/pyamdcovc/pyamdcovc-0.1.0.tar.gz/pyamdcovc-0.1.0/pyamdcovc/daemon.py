
import json
import numpy as np
import sys
import time
import traceback

import argh
from argh import arg, dispatch_command, expects_obj
from scipy.interpolate import interp1d

from .amdcovc import AMDCOVC

class FanCurve():
    def __init__(self, fan_curve_data):
        array = np.array(fan_curve_data, dtype="float64")

        if len(array.shape) != 2 or array.shape[1] != 2:
            raise ValueError("fan curve must be Nx2 array")

        self._interpolator = interp1d(
            x=array[:, 0],
            y=array[:, 1],
            kind="linear",
            fill_value=(0.0, 1.0),
            bounds_error=False,
            assume_sorted=False,
        )

    def get_fan_speed(self, temperature: float) -> float:
        """Get fan speed given ``temperature``."""
        return float(self._interpolator(temperature))

# FIXME: different fan curves for different graphics cards
@arg("--fan-curve", type=str, required=True)
@expects_obj
def main(A):
    fan_curve = json.loads(A.fan_curve)

    fc = FanCurve(fan_curve)
    amd = AMDCOVC()

    while True:
        try:
            for key, adapter in amd.adapters.items():
                T = adapter.temperature
                old_speed = adapter.fan_speed
                speed = fc.get_fan_speed(T)
                print(
                    "# adapter={!r} T_celsius={:.1f} "
                    "fanspeed={:6.4f} new_fanspeed={:6.4f}".format(
                    key, T, old_speed, speed,
                ), file=sys.stderr)
                adapter.fan_speed = speed
        except Exception:
            traceback.print_exc(file=sys.stderr)
        time.sleep(1)

if __name__ == '__main__':
    argh.dispatch_command(main)


