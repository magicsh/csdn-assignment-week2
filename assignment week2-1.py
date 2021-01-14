#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Lear.Li'

class Student(object):
    count = 0
    def __init__(self, name):
        self.__name = name

    def set_name(self,name):
        self.__name = name
        Student.count += 1
        print('您添加了学生%s，现在班级中有%s名学生' % (self.__name, Student.count))


stu1 = Student('xiaoming')
stu1.set_name('xiaoming')

stu2 = Student('laozhang')
stu2.set_name('laozhang')

stu2 = Student('dawang')
stu2.set_name('dawang')