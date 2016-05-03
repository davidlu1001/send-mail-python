#!/usr/bin/env python
# encoding: utf-8

import os
import subprocess
from datetime import date, datetime, timedelta
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.io import output_file, show, vform
from bokeh.plotting import figure, output_file, show
from bokeh.charts import Line, Bar, output_file, show
#from bokeh.plotting import figure, show, output_file, ColumnDataSource
import numpy as np
import pandas as pd
import pprint
from bokeh.charts import TimeSeries, output_file, show
from bokeh.embed import components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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

month_last_grep = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
os.environ['mon_last']=str(month_last_grep)

# generate attach file
# python vault_list.py msd-staging-log | awk '{if ($3 != 0) printf "%10s %10s %8s %2s\n", $1, $3, $4"MB", $6}'
shell_cmd_ori = "python vault_list.py msd-staging-log | grep $mon_last | awk '{if ($3 != 0) print $1, $3, $4, $6}'"
attach_file = "vault_upload_size_" + month_last + ".txt"
fd = open(attach_file, 'w')

p_ori = subprocess.Popen(shell_cmd_ori, stdout=fd, shell=True)
p_ori.wait()


# generate for html email
shell_cmd = "python vault_list.py msd-staging-log | grep $mon_last | awk '{if ($4 != 0.00) print $1, $4, $6}'"
p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, shell=True)

# bokeh
#output_file("vault_data_table.html", autosave=True)

table_all = []
for line in p.stdout:
    new = line.split()
    table_all.append(new)

# numpy to transform row and colomn
table_all_trans = np.array(table_all).T.tolist()

table_dict = dict(
    dates = table_all_trans[0],

    # size: str to float
    size = [float(x) for x in table_all_trans[1]],
    file = table_all_trans[2],

    # temp get category from filename & change '2016' to 'logstash' for stat
    #category = [x.replace('2016', 'logstash') for x in [x.split('/')[0] for x in table_all_trans[2]]],
    #category = [x.split('/')[0] for x in table_all_trans[2]],

    # f5 / syslog / beats
    #category = [[x.split('/')[0], x.split('/')[-1].split('.')[0]] for x in table_all_trans[2]],
    #category = [x.split('/')[-1].split('.')[0] for x in table_all_trans[2]],
    #cate_more = [x[1][0:2] if x[0]=='F5' else x[1] for x in category],
    category = ['f5' if 'f5' in x else x.split('/')[-1].split('.')[0] for x in table_all_trans[2]],
)


# for sum size stat
#pprint.pprint(table_dict)

df = pd.DataFrame(table_dict)
#pprint.pprint(df)
#print(type(df))

# sum size group by date
grouped_date = df['size'].groupby(df['dates'])
result_sum_date = grouped_date.sum()
#pprint.pprint(result_sum_date)
#result_sum_date.plot.line()
#plt.savefig('/Users/davidlu/line.jpg')

output_file("/Users/davidlu/lines.html", title="Vault Upload File Size by Date")
#p = Line(result_sum_date, title="Vault Upload File Size by Date", xlabel='Date', ylabel='Size(MB)', width=400, height=400)
p = Line(result_sum_date, title="Vault Upload File Size by Date", xlabel='Date', ylabel='Size(MB)')
show(p)

#result_sum_date_df = pd.DataFrame(result_sum_date)

#pprint.pprint(result_sum_date)
#print(type(result_sum_date))

#result_sum_date.plot.line()

# sum size group by file category
grouped_cate = df['size'].groupby(df['category'])
result_sum_cate = grouped_cate.sum()

# TimeSeries to DataFrame
result_sum_cate_df=result_sum_cate.to_frame()
#pp = Bar(result_sum_cate_df, title='Total Size by Category', xlabel="Category", ylabel="Size(MB)", width=400, height=400)
pp = Bar(result_sum_cate_df, title='Total Size by Category', xlabel="Category", ylabel="Size(MB)")
output_file("/Users/davidlu/bar.html", title="Vault Upload File Size by Category")
show(pp)

#pprint.pprint(result_sum_cate)
#print(type(result_sum_cate))
#result_sum_cate_df = pd.DataFrame(result_sum_cate)
#pprint.pprint(result_sum_cate_df)
#print(type(result_sum_cate_df))

#result_sum_cate.plot.pie(colors=['r', 'g', 'b', 'c'], autopct='%.2f', fontsize=12, figsize=(6, 6))
#result_sum_cate.plot.pie(title='Category Size', legend=True, colors=['r', 'g', 'b', 'c'], autopct='%.2f', fontsize=12, figsize=(6, 6))
#plt.savefig('/Users/davidlu/pie.jpg')


# gen html table
#source = ColumnDataSource(table_dict)
#columns = [
#    TableColumn(field="dates", title="Date"),
#    TableColumn(field="size", title="Size (MB)"),
#    TableColumn(field="file", title="File"),
#]
#data_table = DataTable(source=source, columns=columns, width=1050, height=280)
##show(data_table)


#script, div = components(data_table)
#html_result = ''' '''

# graph
#p = figure(plot_width=400, plot_height=400)

#
## add both a line and circles on the same plot
#
#p.line(x_list, y_list, line_width=1)
##p.circle(x, y, fill_color="white", size=8)
#
#show(p)

#output_file("timeseries.html")
#data_01 = result_sum_date.to_dict()
#pprint.pprint(data_01)
#p_01 = TimeSeries(data_01, index='dates', title="File Size", ylabel='Size')
#show(p_01)
