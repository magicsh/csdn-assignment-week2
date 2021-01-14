#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Lear.Li'

import time

def metric(fn):

    start_time = time.time()
    end_time = time.time()

    print('耗时：{:.4f}s'.format(end_time - start_time))

    return fn

@metric
def animal_name(name1):
    if name1 == '小猫' :
        print('它的名字叫猫咪')
    elif name1 == '小狗' :
        print('它的名字叫旺财')
    elif name1 == '小鸟' :
        print('它的名字叫唧唧')
    else:
        print('您选择了错误的动物')

animal_name('小猫')