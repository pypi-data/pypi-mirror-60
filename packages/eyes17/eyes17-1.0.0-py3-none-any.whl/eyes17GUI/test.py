# Program starts here
import eyes17.eyes as eyes
p = eyes.open(verbose=1)
if p != None: 
	p.set_sine(1000)
	p.set_sqr1(-1)
	p.set_pv1(0)
	p.set_pv2(0)
	p.set_state(SQR1=1)

while 1:
	print(p.get_state('SEN'))
