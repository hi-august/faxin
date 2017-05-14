# coding=utf-8

import re
from settings import MONGODB_URL
import pymongo
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# import time
# import datetime
import pdb

db = pymongo.MongoClient(MONGODB_URL).faxin.court
# db = pymongo.MongoClient().faxin.court
# db_local = pymongo.MongoClient().faxin.court

name_map = {
    u'请求': 'claim',
    u'诉称': 'accuser_hold_that',
    u'辩称': 'defense_hold_that',
    u'法院查明': 'court_find',
    u'法院认为': 'court_hold_that',
    u'争议焦点': 'focus',
    u'判决如下': 'result',
    u'书记员': 'clerk',
    u'审判员': 'judiciary',
    u'审判长': 'chief_judge',
}

regexes = [re.compile(m) for m in [
    u'终结', u'审结',
    u'诉讼请求', u'诉称', u'诉请', u'起诉', # 诉讼请求 one
    u'上诉请求',
    # u'事实\S*理由', # 诉讼请求之后
    u'辩称', u'未到庭', u'未出庭', u'未答辩',  # 被告辩称
    u'原告\S*证据', u'法庭\S*质证', u'审理查明', u'确认\S*案件事实'
    u'原审法院查明', u'一审法院认定事实', u'原审法院认为', # two
    u'一审法院查明', u'一审法院认定事实', u'一审法院认为', # two
    u'不服\S*上诉', u'不服\S*诉称',
    u'被上诉人\S*答辩',
    u'审理查明\S*事实',
    u'本院认为',
    u'争议焦点', u'判决如下',
    u'第三人\S*称',u'第三人\S*诉',u'第三人\S*请求',
    u'书记员', u'审判员', u'审判长',
    u'号',
]]

def name_check(check, content, item):
    court_proceeding = item.get('court_proceeding', '')
    print(court_proceeding)
    case_raw = item['case_raw']
    # case_id = item.get('case_id', '')
    # if court_proceeding == u'二审':
        # pass
    # elif court_proceeding == u'一审':
        # pass
    clean_data = {}
    clean_data['case_raw'] = case_raw
    flag, flag2, flag3, flag5, flag6, flag7, flag8 = 0, 0, 0, 0, 0, 0, 0
    tmp2 = []
    for x, y in check.items():
        c = min(y)
        # pdb.set_trace()
        if (x in [u'审结', u'终结']):
            # 审理经过
            clean_data['trial'] = content[c]
            flag8 = c
        elif (u'号' in x):
            flag7 = c + 1
        elif (x in [u'辩称', u'未答辩', u'未出庭', u'未到庭']):
            if x in [u'未答辩', u'未出庭', u'未到庭']:
                try:
                    tmp = min([{len(content[b]):b} for b in y]).values()[0]
                    # pdb.set_trace()
                    clean_data['defense_hold_that'] = content[tmp]
                except:
                    clean_data['defense_hold_that'] = content[c]
            else:
                clean_data['defense_hold_that'] = content[c]
            # pdb.set_trace()
        elif (x in [u'诉讼请求', u'诉称', u'诉请', u'起诉']) and (court_proceeding == u'一审'):
            tmp = content[c]
            if u'。事实' in tmp and (court_proceeding == u'一审'):
                # clean_data['claim'] = tmp[:tmp.index('。事实')] + '。'
                clean_data['accuser_hold_that'] = tmp[:tmp.index('。事实')] + '。'
                clean_data['fact_and_reason'] = tmp[tmp.index('。事实'):][1:]
            else:
                clean_data['accuser_hold_that'] = tmp
                # if not clean_data.get('accuser_hold_that', '') and (court_proceeding == u'二审'):
                    # clean_data['accuser_hold_that'] = tmp
            # pdb.set_trace()
        elif (x in [u'上诉请求',]) and (court_proceeding == u'二审'):
            tmp = content[c]
            if u'。事实' in tmp and (court_proceeding == u'一审'):
                # clean_data['claim'] = tmp[:tmp.index('。事实')] + '。'
                clean_data['accuser_hold_that'] = tmp[:tmp.index('。事实')] + '。'
                clean_data['fact_and_reason'] = tmp[tmp.index('。事实'):][1:]
            else:
                if not clean_data.get('accuser_hold_that', '') and (court_proceeding == u'二审'):
                    clean_data['accuser_hold_that'] = tmp
        elif (u'原审法院认为' in x or u'一审法院认为' in x) and (court_proceeding == u'二审'):
            clean_data['origin_court_think'] = content[c]
            # flag2 = c
            flag3 = c
        elif (u'原审法院查明' in x or u'一审法院查明' in x or u'原审法院认定事实' in x or u'一审法院认定事实' in x) and (court_proceeding == u'二审'):
            # flag3 = c
            # pdb.set_trace()
            flag2 = c
        elif (u'不服' in x) and (court_proceeding == u'二审'):
            clean_data['accuser_hold_that'] = content[c]
        elif (u'本院认为' in x):
            flag6 = c
            # clean_data['court_find'] = content[c]
        elif (u'被上诉人' in x) and (court_proceeding == u'二审'):
            clean_data['defense_hold_that'] = content[c]
        elif (u'审理查明' in x) and (court_proceeding == u'二审'):
            flag5 = min(y)
            # clean_data['court_find'] = content[c]
        # elif x == u'诉称':
        elif (u'第三人' in x) and (court_proceeding == u'一审'):
            clean_data['third_hold_that'] = content[c]
        elif (u'证据' in x) or (u'质证' in x) or (u'查明' in x) or (u'事实' in x) and (court_proceeding == u'一审'):
            # pdb.set_trace()
            flag5 = c
            # clean_data['court_find'] = content[c]
        elif x == u'判决如下':
            if '依照' in case_raw:
                clean_data['judges_basis'] = case_raw[case_raw.rindex('依照'):]
            elif '根据' in case_raw:
                clean_data['judges_basis'] = case_raw[case_raw.rindex('根据'):]
            elif '依据' in case_raw:
                clean_data['judges_basis'] = case_raw[case_raw.rindex('依据'):]
            elif '法院认为' in case_raw:
                clean_data['judges_basis'] = case_raw[case_raw.rindex('法院认为'):]
            else:
                print case_raw
                # pdb.set_trace()

            # tmp = case_raw.split('；')[-1]
            # tmp7 = case_raw.split('。')[-1]
            # item
            # if (u'判决如下' in tmp) or (u'判决如下' in tmp7):
                # if u'判决如下' in tmp:
                    # clean_data['judges_basis'] = tmp
                # else:
                    # clean_data['judges_basis'] = tmp7
            # else:
                # clean_data['judges_basis'] = case_raw
            flag = c + 1
        elif x == u'书记员':
            tmp2.append(c)
            clean_data['clerk'] = content[c].strip()
            clean_data['judge_date'] = content[max(y)-1]
        elif x == u'审判长':
            tmp2.append(max(y))
            clean_data['chief_judge'] = content[max(y)].strip()
        elif x == u'审判员':
            tmp2.append(max(y))
            clean_data['judiciary'] = content[max(y)].strip()

    if flag and tmp2:
        try:
            clean_data['result'] = content[flag: min(tmp2)]
        except:
            pass
    # pdb.set_trace()
    if flag2 and flag3:
        try:
            clean_data['origin_court_find'] = '|'.join(content[flag2: flag3])
        except:
            pass
    if flag5 and flag6:
        try:
            if (court_proceeding == u'二审'):
                clean_data['origin_court_find'] = '|'.join(content[flag5 :flag6])
            elif (court_proceeding == u'一审'):
                clean_data['court_find'] = '|'.join(content[flag5 :flag6])
        except:
            pass
    if flag7 and flag8:
        try:
            clean_data['basic_info'] = content[flag7: flag8]
        except:
            pass

    # else:
        # clean_data['result'] = content[max(y)]
    return clean_data

def deal_court_clear_data():
    # for item in db.find({'finished': {'$in': [1]}}).batch_size(30):
    for item in db.find(
            {'finished': {'$in': [2, 3]}},
            # {'doc_id': 'ffaeb330-d20a-473f-ba71-f4850b94fc1b'},
            no_cursor_timeout=False
    ):
        # db.update({'doc_id': item['doc_id']}, {'$unset': {'clean_data': 1}})
        # continue
        clean_data = {}
        content = item.get('content', [])
        # pdb.set_trace()
        if not content:
            continue
        if content[0]:
            sub_case_name = '\n'.join(content[0:2])
        elif not content[0] and content[1]:
            sub_case_name = '\n'.join(content[1:3])
        check = {}
        clean_data = {}
        # pdb.set_trace()
        for p in content:
            if p:
                for regex in regexes:
                    rm_empty_tmp = ''.join(p.split())
                    if regex.search(rm_empty_tmp):
                        k = regex.search(rm_empty_tmp).group(0)
                        i = content.index(p)
                        if k in check:
                            check[k].append(i)
                        else:
                            check[k] = [i, ]
                    if regex.match(rm_empty_tmp):
                        k = regex.match(rm_empty_tmp).group(0)
                        check[k] = []
                        i = content.index(p)
                        if k in check:
                            check[k].append(i)
                        else:
                            check[k] = [i, ]
                        # print name_map[k], k, i
        # pdb.set_trace()
        clean_data = name_check(check, content, item)

        clean_data['sub_case_name'] = sub_case_name
        new = {'clean_data': clean_data, 'finished': 3}
        db.update_one({'doc_id': item['doc_id']}, {'$set': new})
        print(item['doc_id'])
        # pdb.set_trace()

deal_court_clear_data()
