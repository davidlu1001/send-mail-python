#!/usr/bin/env python
# encoding: utf-8

import subprocess
from tabulate import tabulate

# Testing cmd
#p = subprocess.Popen("grep '2016' test_vault_log | awk '{print $1, $2}'", stdout=subprocess.PIPE, shell=True)

shell_cmd = "grep '2016' test_vault_log | awk '{print $1, $2}'"
p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, shell=True)

table_all = []
headers = ["date", "size (MB)"]

for line in p.stdout:
    new = line.split()
    table_all.append(new)

#print tabulate(table_all, headers, tablefmt="psql")
print tabulate(table_all, headers, tablefmt="html")
