#!/bin/python

import sys
import os

found_it = False
new_list = []
for x in sys.argv[1:]:
    binary = x.split("/")[-1]
    new_binary = "."+binary+".cilksan"
    cilkview_path = "/".join(x.split("/")[:-1])+"/"+new_binary
    if os.path.exists("/".join(x.split("/")[:-1])+"/"+new_binary):
        new_list.append(cilkview_path)
        found_it = True
    else:
        new_list.append(x)
if not found_it:
    print 'echo "failed to bind a cilkscale instrumented binary."'
    quit()
print " ".join(new_list)

