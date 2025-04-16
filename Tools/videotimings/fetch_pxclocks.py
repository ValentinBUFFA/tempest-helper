import js2py
js2py.translate_file('videotimings.js', 'videotimings.py')

from videotimings import *

print('["cvt", "cvt_rb", "cvt_rb2", "dmt", "cea"]')
pxclocks, htotals, vtotals = videotimings.compute_pxclock(1920, 1080, 60)
print(pxclocks, htotals, vtotals)