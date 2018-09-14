#!/bin/python

import sys
import os


found_it = False
new_list = []
for x in sys.argv[1:]:
    binary = x.split("/")[-1]
    new_binary = "."+binary+".cilkscale"
    cilkview_path = "/".join(x.split("/")[:-1])+"/"+new_binary
    if os.path.exists("/".join(x.split("/")[:-1])+"/"+new_binary):
        found_it = True
        new_list.append(cilkview_path)
    else:
        new_list.append(x)
if not found_it:
    print 'echo "failed to bind a cilkscale instrumented binary."'
    quit()
print " ".join(new_list)

