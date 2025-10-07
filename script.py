with open('app.py', 'r') as f:
    lines = f.readlines()
half = len(lines) // 2
with open('app_new.py', 'w') as f2:
    f2.writelines(lines[:half])
import os
os.remove('app.py')
os.rename('app_new.py', 'app.py')
