#!/usr/bin/env python
# encoding: utf-8

import subprocess
from datetime import date, datetime, timedelta
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.io import output_file, show, vform
from bokeh.plotting import figure, output_file, show
#from bokeh.plotting import figure, show, output_file, ColumnDataSource
import numpy as np
import pandas as pd
import pprint


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

# bokeh
output_file("vault_data_table.html", autosave=True)

table_all = []
for line in p.stdout:
    new = line.split()
    table_all.append(new)

# numpy to transform row and colomn
table_all_trans = np.array(table_all).T.tolist()

table_dict = dict(
    dates=table_all_trans[0],
    # size: str to float
    size=[float(x) for x in table_all_trans[1]],
    file=table_all_trans[2],
    # get category from filename & change '2016' to 'logstash' for stat
    category=[x.replace('2016', 'logstash') for x in [x.split('/')[0] for x in table_all_trans[2]]],
)


# for sum size stat
df = pd.DataFrame(table_dict)

# sum size group by date
grouped_date = df['size'].groupby(df['dates'])
result_sum_date = grouped_date.sum()

# sum size group by file category
grouped_cate = df['size'].groupby(df['category'])
result_sum_cate = grouped_cate.sum()
#pprint.pprint(result_sum_cate)
#print(type(result_sum_cate))
#result_sum_cate_df = pd.DataFrame(result_sum_cate)
#pprint.pprint(result_sum_cate_df)
#print(type(result_sum_cate_df))


# gen html table
#source = ColumnDataSource(table_dict)
#columns = [
#    TableColumn(field="dates", title="Date"),
#    TableColumn(field="size", title="Size (MB)"),
#    TableColumn(field="file", title="File"),
#]
#data_table = DataTable(source=source, columns=columns, width=1050, height=280)
#show(data_table)

# graph
#p = figure(plot_width=400, plot_height=400)

# add both a line and circles on the same plot
#p.line(result_sum_cate_df, line_width=1)
#p.circle(x, y, fill_color="white", size=8)

#show(p)
