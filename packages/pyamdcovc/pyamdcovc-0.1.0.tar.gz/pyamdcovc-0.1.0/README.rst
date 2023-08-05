
pyamdcovc
=========

Control AMD graphics card from Python.

Includes a daemon mode which manually controls the fan using a
user-input fan curve.

Example::

    from pyamdcovc import AMDCOVC

    amd = AMDCOVC()
    adapters = amd.adapters
    for key, adapter in adapters.items():
        print("card ID", key)
        print("  temperature:", adapter.temperature)
        print("  fan speed (between 0 and 1):", adapter.fan_speed)

        # adapter.fan_speed = 0.5 # set fan level to 50%

