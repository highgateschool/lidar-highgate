import os
import os.path as op
import re

mypath = os.getcwd()

onlyfiles = [f for f in os.listdir(mypath) if op.isfile(op.join(mypath, f))]

onlyasc = [f for f in onlyfiles if re.search('\.asc$', f)]

print(onlyasc)
