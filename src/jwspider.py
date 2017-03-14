# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import sys
import xml.etree.cElementTree as Et
import urllib
import urllib.parse
import urllib.error
import urllib.request
import http.cookiejar
import re


class RedirctHandler(urllib.request.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        pass


class JWSpider(object):

    def __init__(self):
        self.cookie = http.cookiejar.LWPCookieJar()
        self.cookie_support = urllib.request.HTTPCookieProcessor(self.cookie)
        self.login_msg = ""
        self.is_login = False
        pass

    def build_opener(self):
        debug_handler = urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(debug_handler, RedirctHandler,
                                             urllib.request.HTTPCookieProcessor(self.cookie))
        return opener

    def login_validate(self, stucode, passwd):
        """
        登录校验
        :param stucode: 学号
        :param passwd: 密码
        :return:
        """
        header = {
            'User-Agent': 'WeJudge.JWConnector/1.1',
            'Accept': 'text/html',
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://es.bnuz.edu.cn/"
        }
        data = '__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%%2FwEPDwUKLTc1NTY5NDcxNA9kFgICAQ9kFgICDw8PZBYCHgdvbmNsaWNrBQ93aW5kb3cuY2xvc2UoKTtkZCz5uRg%%2BGWXj6yrZOl43a%%2FLUmaQB&__VIEWSTATEGENERATOR=09394A33&__PREVIOUSPAGE=P41Qx-bOUYMcrSUDsalSZQ66PXL-H_8xeQ4t7bJ3gWnYCDI-j8Z8SOoK8eM1&__EVENTVALIDATION=%%2FwEWCwLbuJfUBALs0bLrBgLs0fbZDAK%%2FwuqQDgKAqenNDQLN7c0VAveMotMNAu6ImbYPArursYYIApXa%%2FeQDAoixx8kBymXan4ObCW11IybkO9%%2B%%2BMz1AoJ8%%3D&TextBox1=%s&TextBox2=%s&RadioButtonList1=%%E5%%AD%%A6%%E7%%94%%9F&Button4_test='
        post_data = data % (stucode, passwd)
        req = urllib.request.Request("http://es.bnuz.edu.cn/default2.aspx", headers=header, data=post_data.encode("utf-8"))
        opener = self.build_opener()
        try:
            web = opener.open(req)
            ctx = web.read().decode("utf-8")
            if u"密码不正确" in ctx:
                self.login_msg = "密码不正确"
            elif u"5分钟" in ctx:
                self.login_msg = "因验证接口密码错误限制，请5分钟以后再试"
            else:
                self.login_msg = "登录失败"
            self.is_login = False
            return False
        except urllib.error.URLError as e:
            if hasattr(e, 'code') and e.code == 302:
                if 'error' in e.info().get('Location'):
                    self.login_msg = "登录失败"
                    self.is_login = False
                    return False
                self.login_msg = ""
                self.is_login = True
                return True
            else:
                self.login_msg = "未知错误"
                self.is_login = False
                return False

    def get_student_info(self):
        if not self.is_login:
            return None
        req = urllib.request.Request("http://es.bnuz.edu.cn/jwgl/xsgrxx.aspx", headers = {
            'User-Agent': 'WeJudge.ESConnector/1.0',
            'Accept': 'text/html',
            "Referer": "http://es.bnuz.edu.cn/"
        })

        student_infos = {}
        opener = self.build_opener()
        web = opener.open(req)
        data = web.read().decode("utf-8")
        # 性别
        pattern = re.compile('<span id="lbl_xb">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['gender'] = match.group(1) if match is not None else ""
        # 姓名
        pattern = re.compile('<span id="xm">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['name'] = match.group(1) if match is not None else ""
        # 姓名
        pattern = re.compile('<span id="lbl_Xmpy">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['name_pinyin'] = match.group(1) if match is not None else ""
        # 生日
        pattern = re.compile('<span id="lbl_csrq">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['birthday'] = match.group(1) if match is not None else ""
        # 家庭住址
        pattern = re.compile('<span id="lbl_jtdz">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['address'] = match.group(1) if match is not None else ""
        # 行政班级
        pattern = re.compile('<span id="lbl_xzb">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['className'] = match.group(1) if match is not None else ""
        # 学院
        pattern = re.compile('<span id="lbl_xy">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['depName'] = match.group(1) if match is not None else ""
        # 专业
        pattern = re.compile('<span id="lbl_zymc">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['enrollSpecialityName'] = match.group(1) if match is not None else ""
        # 年级
        pattern = re.compile('<span id="lbl_dqszj">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['grade'] = match.group(1) if match is not None else ""
        # 身份证号码
        pattern = re.compile('<span id="lbl_sfzh">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['id_card'] = match.group(1) if match is not None else ""
        # 毕业中学
        pattern = re.compile('<span id="lbl_byzx">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['high_school'] = match.group(1) if match is not None else ""
        # 学历层次
        pattern = re.compile('<span id="lbl_CC">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['graduate_level'] = match.group(1) if match is not None else ""
        # 民族
        pattern = re.compile('<span id="lbl_mz">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['nation'] = match.group(1) if match is not None else ""
        # 来源省份
        pattern = re.compile('<span id="lbl_lys">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['province'] = match.group(1) if match is not None else ""
        # 来源地区
        pattern = re.compile('<span id="lbl_lydq">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['city'] = match.group(1) if match is not None else ""

        return student_infos


class JWFZSpider(object):

    def __init__(self):
        self.cookie = http.cookiejar.LWPCookieJar()
        self.cookie_support = urllib.request.HTTPCookieProcessor(self.cookie)
        self.login_msg = ""         # 如果出现错误，可以在这里取得信息
        self.is_login = False       # 认证是否成功，就在这里显示
        pass

    def build_opener(self):
        debug_handler = urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(
            debug_handler,
            RedirctHandler,
            urllib.request.HTTPCookieProcessor(self.cookie)
        )
        return opener

    def login_validate(self, stucode, passwd):
        """
        登录校验
        :param stucode: 学号
        :param passwd: 密码
        :return:
        """
        header = {
            'User-Agent': 'WeJudge.JWFZConnector/1.0',
            'Accept': 'text/html',
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://es.bnuz.edu.cn:8080/"
        }
        data = {
            "tssName": stucode,
            "tssPassword": passwd
        }
        req = urllib.request.Request("http://es.bnuz.edu.cn:8080/login.do",
                                     headers=header,
                                     data=urllib.parse.urlencode(data).encode("utf-8"))
        opener = self.build_opener()
        web = opener.open(req)
        ctx = web.read().decode("gbk")
        if "用户名或密码不正确" in ctx:
            self.login_msg = "密码不正确"
            self.is_login = False
            return False
        else:
            self.is_login = True
            return True
            
if __name__ == '__main__':
    # ===== 教务辅助系统认证：http://es.bnuz.edu.cn:8080/（没有密码错误的等待限制）

    b = JWFZSpider()
    print(b.login_validate("学号", "密码"))   # 登录认证成功返回True


    # ===== 教务系统认证：http://es.bnuz.edu.cn/ （这个破接口有输错一次密码停5分钟的问题，不建议用，
    # 或者建议配合上面的辅助系统的认证来确保这一步认证正确
    # a = JWSpider()
    # if a.login_validate("学号", "密码"):
    #     print("Success")
    #     print(a.get_student_info())     # 拉取学生信息，以JSON形式返回
    # else:
    #     print(a.login_msg)          # 反馈登录失败的问题