import sys
import os


new_list = []
for x in sys.argv[1:]:
    binary = x.split("/")[-1]
    new_binary = "."+binary+".cilkview"
    cilkview_path = "/".join(x.split("/")[:-1])+"/"+new_binary
    if os.path.exists("/".join(x.split("/")[:-1])+"/"+new_binary):
        new_list.append(cilkview_path)
    else:
        new_list.append(x)
print " ".join(new_list)

