# coding=utf-8

import re
from settings import MONGODB_URL
import pymongo
import json
# import time
# import datetime
import pdb

db = pymongo.MongoClient(MONGODB_URL).faxin.faxin_new
db_local = pymongo.MongoClient().faxin.court
# pdb.set_trace()

num_new_map = {
    u'一': 1,
    u'二': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,
}
num_map = {
    1: u'一',
    2: u'二',
    3: u'三',
    4: u'四',
    5: u'五',
    6: u'六',
    7: u'七',
    8: u'八',
    9: u'九',
    10: u'十',
    11: u'十一',
    12: u'十二',
    13: u'十三',
    14: u'十四',
    15: u'十五',
    16: u'十六',
    17: u'十七',
    18: u'十八',
    19: u'十九',
    20: u'二十',
    21: u'二十一',
    22: u'二十二',
    23: u'二十三',
    24: u'二十四',
    25: u'二十五',
    26: u'二十六',
    27: u'二十七',
    28: u'二十八',
    29: u'二十九',
    30: u'三十',
    31: u'三十一',
    32: u'三十二',
    33: u'三十三',
    34: u'三十四',
    35: u'三十五',
    36: u'三十六',
    37: u'三十七',
    38: u'三十八',
    39: u'三十九',
    40: u'四十',
    41: u'四十一',
    42: u'四十二',
    43: u'四十三',
    44: u'四十四',
    45: u'四十五',
    46: u'四十六',
    47: u'四十七',
    48: u'四十八',
    49: u'四十九',
    50: u'五十',
    51: u'五十一',
    52: u'五十二',
    53: u'五十三',
    54: u'五十四',
    55: u'五十五',
    56: u'五十六',
    57: u'五十七',
    58: u'五十八',
    59: u'五十九',
    60: u'六十',
}

regexes = [re.compile(m) for m in [
    u'第\S+章','u第\S+条', u'第\S+节',
]]

def deal_with_content(tmp, first=u'第', default=u'章', is_key=False):
    '''获取具体章节'''
    bar_list = []
    for i, x in enumerate(tmp):
        if re.search(ur'%s[一二三四五六七八九十零百千]{1,}%s'%(first, default), x):
            k = re.search(ur'%s[一二三四五六七八九十零百千]{1,}%s'%(first, default),x).group(0)
            if default in x:
                new = {'index': i, 'name': x}
                if is_key:
                    pre_value = x.replace(k, '')
                    new  = {'index': i, 'name': k, 'value': [pre_value]}
                bar_list.append(new)
                # return new
    return bar_list

def deal_with_chapter(cha_list, tmp):
    '''取得具体值'''
    res = []
    for i, x in enumerate(cha_list):
        try:
            value = tmp[x['index']+ 1: cha_list[i+1]['index']]
        except:
            value = tmp[x['index']+ 1: ]
        if x.get('value', []):
            x.get('value', '').extend(value)
            new = {'value':  x.get('value'), 'index': x['index'], 'name': x['name']}
        else:
            new = {'value': value, 'index': x['index'], 'name': x['name']}
        keys = [key.get('name', '') for key in res]
        if new['name'] not in keys:
            res.append(new)
        else:
            for ii, y in enumerate(res):
                if y[u'name'] == new['name']:
                    res[ii].update(new)
    return res

def deal_faxin_clean_data():
    for item in db.find({
            # 'finished': {'$in': [2]},
            # 'gid': 'A243314',
            'gid': 'A234085',
    }).batch_size(30):
        clean_data = {}
        content = item.get('content', [])
        # check = {}
        clean_data = []
        cha_list = deal_with_content(content)
        # 取得章的列表索引
        if cha_list and len(cha_list) > 5:
            print(111)
            tmp2 = {}
            cha_content = deal_with_chapter(cha_list, content)
            if cha_content:
                for x in cha_content:
                    # pdb.set_trace()
                    if not x['value']:
                        continue
                    bar_list = deal_with_content(x['value'], first=u'第', default=u'条', is_key=True)
                    if bar_list:
                        sub_value = deal_with_chapter(bar_list, x['value'])
                        for i, z in enumerate(sub_value):
                            sub_value[i]['value'] = ''.join(z['value']).strip()
                            sub_value[i].pop('index', None)
                        tmp2 = {'chapter': x['name'], 'data': sub_value}
                        clean_data.append(tmp2)
        else:
            print(222)
            tmp2 = {}
            bar_list = deal_with_content(content, u'条', is_key=True)
            if bar_list:
                sub_value = deal_with_chapter(bar_list, content)
                for i, z in enumerate(sub_value):
                    sub_value[i]['value'] = ''.join(z['value']).strip()
                    sub_value[i].pop('index', None)
                # tmp2 = {'chapter': z['name'], 'data': sub_value}
                # print(222)
                # pdb.set_trace()
                clean_data = sub_value
        if len(clean_data) < 5:
            tmp2 = {}
            bar_list = deal_with_content(content, first=u'', default=u'、', is_key=True)
            # bar_list = deal_with_content(content, first=u'第', default=u'章', is_key=True)
            if bar_list:
                sub_value = deal_with_chapter(bar_list, content)
                for i, z in enumerate(sub_value):
                    sub_value[i]['value'] = ''.join(z['value']).strip()
                    sub_value[i].pop('index', None)
                clean_data = sub_value


        print(item['gid'], 111)
        if not clean_data:
            print('%s clean_data is failed'%item['gid'])
            continue
        try:
            key = num_map[len(clean_data)]
        except:
            key = num_map[60]
            # pdb.set_trace()
            pass
        last_one = clean_data[-1].get('chapter', '')
        if not last_one:
            last_one = clean_data[-1].get('name', '')
        new_key = ''
        for b in last_one:
            if num_new_map.get(b, 0):
                new_key += str(num_new_map.get(b, 0))
        pdb.set_trace()
        if (key not in last_one) and (int(new_key) != len(clean_data)):
            print(item['gid'], key, new_key)
            pdb.set_trace()
            continue
        new = {'clean_data2': clean_data, 'finished': 3}
        try:
            db.update_one({'gid': item['gid']}, {'$set': new})
        except:
            pdb.set_trace()
        print(item['gid'])
        pdb.set_trace()

# deal_faxin_clean_data()

def deal_faxin_clean_data2():
    for item in db.find({
            'finished': {'$in': [2]},
            # 'gid': 'A243314',
    }).batch_size(30):
        clean_data = {}
        content = item.get('content', [])
        # check = {}
        clean_data = []
        cha_list = deal_with_content(content)
        # 取得章的列表索引
        if cha_list and len(cha_list) > 5:
            print(111)
            tmp2 = {}
            cha_content = deal_with_chapter(cha_list, content)
            if cha_content:
                for x in cha_content:
                    if not x['value']:
                        continue
                    tmp2 = {}
                    bar_list = deal_with_content(x['value'], first=u'第', default=u'条', is_key=True)
                    sec_list = deal_with_content(x['value'], first=u'第', default=u'节', is_key=True)
                    # 有节
                    if sec_list and bar_list:
                        sub_value = deal_with_chapter(sec_list, x['value'])
                        tmp5 = []
                        for i, z in enumerate(sec_list):
                            bar_list = deal_with_content(z['value'][1:], first=u'第', default=u'条', is_key=True)
                            bar_content = deal_with_chapter(bar_list, z['value'][1:])
                            for ii, zz in enumerate(bar_content):
                                bar_content[ii]['value'] = ''.join(zz['value']).strip()
                                bar_content[ii].pop('index', None)
                                bar_content[ii]['selection'] = z['name']
                                bar_content[ii]['selection_value'] = z['value'][0]
                            tmp5.append(bar_content)
                        tmp3 = {'selections': tmp5}
                        tmp2 = {'chapter': x['name'], 'data': tmp3}
                        clean_data.append(tmp2)

                    elif bar_list:
                        sub_value = deal_with_chapter(bar_list, x['value'])
                        for i, z in enumerate(sub_value):
                            sub_value[i]['value'] = ''.join(z['value']).strip()
                            #  sub_value[i].get('value', []).extend(z['value'])
                            sub_value[i].pop('index', None)
                        tmp2 = {'chapter': x['name'], 'data': sub_value}
                        keys = [key.get('chapter', '') for key in clean_data]
                        if x['name'] not in keys:
                            clean_data.append(tmp2)
                        else:
                            for ii, y in enumerate(clean_data):
                                if y[u'chapter'] == x[u'name']:
                                    clean_data[ii].update(tmp2)
                    # 只有节
                    elif not bar_list and sec_list:
                        #  pdb.set_trace()
                        sub_value = deal_with_chapter(sec_list, x['value'])
                        for i, z in enumerate(sub_value):
                            sub_value[i]['value'] = ''.join(z['value']).strip()
                            sub_value[i].pop('index', None)
                        tmp2 = {'chapter': x['name'], 'data': sub_value}
                        if x['name'] not in keys:
                            clean_data.append(tmp2)
                        else:
                            for ii, y in enumerate(clean_data):
                                if y[u'chapter'] == x[u'name']:
                                    clean_data[ii].update(tmp2)
                    else:
                        tmp2 = {'chapter': x['name'], 'data': x['value']}
                        if x['name'] not in keys:
                            clean_data.append(tmp2)
                        else:
                            for ii, y in enumerate(clean_data):
                                if y[u'chapter'] == x[u'name']:
                                    clean_data[ii].update(tmp2)
        else:
            print(222)
            tmp2 = {}
            bar_list = deal_with_content(content, first=u'第', default=u'条', is_key=True)
            sec_list = deal_with_content(content, first=u'第', default=u'节', is_key=True)
            if bar_list:
                sub_value = deal_with_chapter(bar_list, content)
                for i, z in enumerate(sub_value):
                    sub_value[i]['value'] = ''.join(z['value']).strip()
                    sub_value[i].pop('index', None)
                # tmp2 = {'chapter': z['name'], 'data': sub_value}
                # print(222)
                # pdb.set_trace()
                clean_data = sub_value
            elif not bar_list and sec_list:
                #  pdb.set_trace()
                sub_value = deal_with_chapter(sec_list, x['value'])
                for i, z in enumerate(sub_value):
                    sub_value[i]['value'] = ''.join(z['value']).strip()
                    sub_value[i].pop('index', None)
                clean_data = sub_value
        if len(clean_data) < 5:
            tmp2 = {}
            # bar_list = deal_with_content(content, first=u'', default=u'、', is_key=True)
            bar_list = deal_with_content(content, first=u'第', default=u'章', is_key=True)
            if bar_list:
                sub_value = deal_with_chapter(bar_list, content)
                for i, z in enumerate(sub_value):
                    sub_value[i]['value'] = ''.join(z['value']).strip()
                    sub_value[i].pop('index', None)
                clean_data = sub_value


        print(item['gid'], 111)
        if not clean_data:
            print('%s clean_data is failed'%item['gid'])
            continue
        try:
            key = num_map[len(clean_data)]
        except:
            key = num_map[60]
            # pdb.set_trace()
            pass
        last_one = clean_data[-1].get('chapter', '')
        if not last_one:
            last_one = clean_data[-1].get('name', '')
        new_key = ''
        for b in last_one:
            if num_new_map.get(b, 0):
                new_key += str(num_new_map.get(b, 0))
        if not new_key:
            new_key = '0'
        if (key not in last_one) and (int(new_key) != len(clean_data)):
            print(item['gid'], key, new_key)
            continue
            # db.update_one({'gid': item['gid']}, {'$set': new})
            # pdb.set_trace()
        new = {'clean_data': clean_data, 'finished': 2}
        new = {'clean_data': clean_data, 'finished': 5}
        db.update_one({'gid': item['gid']}, {'$set': new})
        print(item['gid'])
        # pdb.set_trace()

deal_faxin_clean_data2()
