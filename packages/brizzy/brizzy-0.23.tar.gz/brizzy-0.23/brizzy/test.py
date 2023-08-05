#!/usr/bin/env python3

import seabreeze.spectrometers as sb
import seabreeze
import time

devices = sb.list_devices()
print(devices)
spec = sb.Spectrometer(devices[0])
print(spec)
retval = spec.tec_set_enable(True)
print(retval)
spec.tec_set_temperature_C(20)
time.sleep(60)
#
#for i in range(4,10):
#    retval = spec.tec_get_temperature_C()
#    print(retval)
#    time.sleep(2)
