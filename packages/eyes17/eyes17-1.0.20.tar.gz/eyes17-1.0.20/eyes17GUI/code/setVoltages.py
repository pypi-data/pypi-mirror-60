#import eyes17.eyes          # uncomment these two lines while running stand-alone
#p = eyes17.eyes.open()

# Connect PV1 to A1 and PV2 to A2, using two wires
from __future__ import print_function

print (p.set_pv1(2.5))
print (p.set_pv2(1))

print (p.get_voltage('A1'))
print (p.get_voltage('A2'))

