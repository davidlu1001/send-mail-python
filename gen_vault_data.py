#!/usr/bin/env python
# encoding: utf-8

import subprocess
from datetime import date, datetime, timedelta
from tabulate import tabulate

# Testing cmd
# p = subprocess.Popen("grep '2016' test_vault_log | awk '{print $1, $2}'", stdout=subprocess.PIPE, shell=True)
# shell_cmd = "grep '2016' test_vault_log | awk '{print $1, $2}'"
# p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, shell=True)

'''
shell_cmd output format:
date, size(bytes), size(MB), filename

2016-04-03 23:29:14         0   0.00 MB logstash/
2016-04-03 23:29:45         0   0.00 MB logstash/2016/
2016-04-04 11:32:21      1198   0.00 MB logstash/2016//tes.py
2016-04-06 00:04:28         4   0.00 MB logstash/2016/04/06/beats.log-20160402.gz
'''
month = datetime.now().strftime('%Y%m')
month_last = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y%m")
today = datetime.now().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(1)).strftime('%Y%m%d')

# generate attach file
# python vault_list.py msd-staging-log | awk '{if ($3 != 0) printf "%10s %10s %8s %2s\n", $1, $3, $4"MB", $6}'
shell_cmd_ori = "python vault_list.py msd-staging-log | awk '{if ($3 != 0) print $1, $3, $4, $6}'"
attach_file = "vault_upload_size_" + month_last + ".txt"
fd = open(attach_file, 'w')

p_ori = subprocess.Popen(shell_cmd_ori, stdout=fd, shell=True)
p_ori.wait()


# generate for html email
shell_cmd = "python vault_list.py msd-staging-log | awk '{if ($4 != 0.00) print $1, $4, $6}'"
p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, shell=True)

table_all = []
headers = ["Date", "Size (MB)", "Filename"]

for line in p.stdout:
    new = line.split()
    table_all.append(new)

# print tabulate(table_all, headers, tablefmt="psql")
print(tabulate(table_all, headers, tablefmt="html"))
