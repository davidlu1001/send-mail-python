#!/usr/bin/env python
# encoding: utf-8

import os
import subprocess
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import pprint
import collections
import json


def date_range(start, stop, step):
    while start < stop:
        yield start
        start += step

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

year_int = int(datetime.now().strftime('%Y'))
month_int = int(datetime.now().strftime('%m'))
day_int = int(datetime.now().strftime('%d'))
month_last_int = int((datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%m"))

month_last_grep = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
os.environ['mon_last']=str(month_last_grep)

# generate attach file
# python vault_list.py msd-staging-log | awk '{if ($3 != 0) printf "%10s %10s %8s %2s\n", $1, $3, $4"MB", $6}'
#shell_cmd_ori = "python vault_list.py msd-staging-log | grep $mon_last | awk '{if ($3 != 0) print $1, $3, $4, $6}'"
shell_cmd_ori = "python vault_list.py msd-staging-log | awk '{if ($3 != 0) print $1, $3, $4, $6}'"
attach_file = "vault_upload_size_" + month_last + ".txt"
fd = open(attach_file, 'w')

p_ori = subprocess.Popen(shell_cmd_ori, stdout=fd, shell=True)
p_ori.wait()


# generate for html email
#shell_cmd = "python vault_list.py msd-staging-log | grep $mon_last | awk '{if ($4 != 0.00) print $1, $4, $6}'"
#shell_cmd = "python vault_list.py msd-staging-log | awk '{if ($4 != 0.00) print $1, $4, $6}'"

os.environ['f5_cate']="F5"
os.environ['file_sep']="."

# combine size with same "date + category"
# remove noise 'audit' and change category name "beats -> app"
shell_cmd = "python vault_list.py msd-staging-log | grep -v audit | awk '{if ($4 != 0.00) print $1, $4, $6}' | awk -F'/' '{print $1, $NF}' | awk -v var1=$f5_cate -v var2=$file_sep '{if($3==var1) print $1, tolower(var1), $2; else { split($4, cate, var2); print $1, cate[1], $2; } }' | awk -v var=$gene_sep '{s[$1 $2] += $3}END{ for(i in s){  print i, s[i] } }' | sort -n -k12 | awk '{print substr($1, 0, 10), substr($1, 11), $2}' | sed -e 's#beats#app#g'"

p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, shell=True)

table_all = []
for line in p.stdout:
    new = line.split()
    table_all.append(new)

# numpy to transform row and colomn
table_all_trans = np.array(table_all).T.tolist()

table_dict = dict(
    dates = table_all_trans[0],
    category = table_all_trans[1],
    # size: str to float
    size = [float(x) for x in table_all_trans[2]],
)

table_dict_line = pd.DataFrame.from_dict(table_dict)
table_dict_ts = table_dict_line.set_index('dates')

# get category
category_set = sorted(list(set(table_dict['category'])))
#category_set = [x.title() for x in sorted(list(set(table_dict['category'])))]
table_ts_list_all = []

# gen last_mon days
dates_last_mon_list = [d.strftime("%Y-%m-%d") for d in date_range(datetime(year_int, month_last_int, 1), datetime(year_int, month_int, day_int), timedelta(days=1))]
#print("date\n{}".format(dates_last_mon_list))

final_result_return = []

final_dict_cate = collections.OrderedDict.fromkeys(sorted(category_set))


# first add 'date'
#final_dict_cate['date'] = dates_last_mon_list

for cate in category_set:
    full_days_dict_def = {key_date: 0.00 for key_date in dates_last_mon_list}
    full_days_dict = collections.OrderedDict(sorted(full_days_dict_def.items()))
    full_days_dict_value = []
    # DataFrame
    i = table_dict_ts[table_dict_ts.category == cate].loc[:, ['size']]
    # Dict, set float precision
    i_dict = i.to_dict()['size']

    # real data
    for index_date in i.index.tolist():
        # full date
        for key_date in full_days_dict.keys():
            if key_date == index_date:
                full_days_dict[key_date] = round(i_dict[index_date], 2)
                break

    # remove date in full_days_dict
    # final_dict_cate[cate] = full_days_dict
    final_dict_cate[cate] = full_days_dict.values()

# Add line for sum based on date
'''
[
(0.84, 0.0, 5.88, 51.03),
(4.24, 0.0, 11.8, 60.15)
]
'''


# fac sum
def factorial(x, n):
    if n == 1:
        return x[n-1]
    if n == 2:
        return x[n-2] + x[n-1]
    else:
        return x[n-1] + factorial(x, n-1)


# sum of cate per day
sum_day = [round(sum(x), 2) for x in zip(*[x for x in final_dict_cate.values()])]

# sum of sum_day factorial
fac_sum = []
for i, z in enumerate(sum_day, 1):
    fac_sum.append(round(factorial(sum_day, i), 2))

# make category Capital for seq
final_dict_cate = {k.title(): v for k, v in final_dict_cate.iteritems()}

# category = 'daysum'
final_dict_cate['daysum'] = sum_day

# category = 'total'
final_dict_cate['total'] = fac_sum
#pprint.pprint(final_dict_cate)


# return json format for replace dashboard.html
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


#final_result_return_dict = {'date': dates_last_mon_list}
#merge_dict = collections.OrderedDict()
#merge_dict = merge_dicts(final_result_return_dict, final_dict_cate)

final_dict_cate['date'] = dates_last_mon_list
json_str = json.dumps(final_dict_cate)

# add header for js json format
json_str_add = "data = '" + json_str + "'"
file_json_data = "/usr/local/var/www/htdocs/data.json"
with open(file_json_data, 'w') as f:
    f.write(json_str_add)
