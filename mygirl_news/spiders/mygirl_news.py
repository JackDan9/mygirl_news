# -*- coding:utf-8 -*-

"""
File: mygirl_news.py
Author: jackdan
Date: 2020/12/25 14:50
Description: Crawl the news information for mygirl news
"""

from __future__ import unicode_literals

from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
import logging
from random import randint
import smtplib
import sys

import scrapy
from scrapy import Request


defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


LOG = logging.getLogger(__name__)


class MygirlNewsSpider(scrapy.Spider):
    """Spider to perform necessary checks to get the network address information of start_urls and
    Format web page information to get the required fields to piece together the mail.
    """
    name = "mygirl_news"
    allow_domains = ['www.pbc.gov.cn']
    start_urls = [
        "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html",
        # "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/4151940/index.html"
        #
        # "http://www.weather.com.cn/weather1d/101180101.shtml",
        # 贵阳
        # "http://www.weather.com.cn/weather1d/101260101.shtml",
    ]

    cookie_dict = {}
    result_data = []
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Referer': 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, headers=self.headers, callback=self.parse, method='POST')

    def parse(self, response):
        """ Parse out the required field information and collect the date of the day, days of
        love, the location of the weather, and the words of love.

        :param response: The response context, for parsing out the required field information.
        :return: Return the information you need.
        """

        content_url_list = response.xpath(
            '//*[@height="22"]/font/a/@href').extract()
        yield Request(url='http://www.pbc.gov.cn' + content_url_list[randint(0, 14)], headers=self.headers, callback=self.parse_data, method='POST')

    def parse_data(self, response):
        """ Parse out the required field information and collect the date of the day, days of
        love, the location of the weather, and the words of love.

        :param response: The response context, for parsing out the required field information.
        :return: Return the information you need.
        """

        today = datetime.today()
        anniversary = datetime(2018, 3, 14)
        loving_days = (today - anniversary).days

        loving_word = '爱你呦！！！'

        content_title = response.xpath('//h2[@style="font-size: 16px;color: #333;"]/text()').extract()
        content_date = response.xpath('//td[@align="right"]/text()').extract()
        if len(content_title) != 0:
            content_html_title = '<h2> 新闻标题: ' + str(content_title[0]) + '</h2>'
        else:
            content_html_title = '<h2 style="font-size: 16px;color: #333;"> 无标题 </h2>'
        
        if len(content_date) != 0:
            content_html_date = '<span><span style="font-weight: bold;">新闻发布日期: <span>' + str(content_date[2]) + '</span>'
        
        content_list = response.xpath('//div[@id="zoom"]/p/text()').extract()
        content_html_list = ''
        if len(content_list) != 0:
            for content in content_list:
                content_html_list = content_html_list + '<p style="display: block; color: #000; margin-block-start: 14px; text-indent: 28px; margin-block-end: 14px;padding-bottom: 15px; text-align: justify; text-justify: inter-word;">' + str(content) + '</p>'
        
        lst = [
            '<html><body style="font-family: cursive;">' + 
            '<h3 style="font-family: cursive; font-weight: 500; font-size: 1.17em;">你好, 仙女大大:<br><br></h3>' + 
            '<h4 style="font-family: cursive; font-weight: 300; font-size: 1em;">今天是' + today.strftime('%Y-%m-%d') + 
            ':<br><br></h4>' +
            '<h4 style="font-family: cursive; font-weight: 300; font-size: 1em;">首先，今天已经是我们相恋的第' + str(loving_days) +
            '天了喔。然后猪猪就要来播送央行新闻了！！<br><br></h4>' +
            '<div style="width: 100%; text-align: center;">' + content_html_title + '</div>' + 
            '<div> <span style="font-weight: bold;">新闻内容: <span>' + content_html_list + '</div>' + 
            '<div style="width: 100%; text-align: left; padding-left: 10px;">' + content_html_date + '</div>' + 
            '<h4 style="font-family: cursive; font-weight: 300; color: red; font-size: 1em;">' + loving_word  + '<br/>' + '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/66.gif">' + 
            '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/65.gif">' + 
            '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/66.gif">' + 
            '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/52.gif">' +  
            '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/65.gif">' + 
            '<img src="https://rescdn.qqmail.com/zh_CN/images/mo/DEFAULT2/52.gif"></h4></body></html>'
        ]
        # It is your aim emali word. 
        mailto_list = "1835812864@qq.com"
        # It is your email host.
        mail_host = "smtp.qq.com"
        # It is your email word.
        mail_user = "1835812864@qq.com"
        # It is your password
        mail_pass = "******************"

        content = ''.join(lst)
        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['From'] = mail_user
        msg['To'] = mailto_list
        msg['Subject'] = Header('猪猪的央行新闻', 'utf-8')

        try:
            s = smtplib.SMTP_SSL(mail_host, 465)
            s.login(mail_user, mail_pass)
            s.sendmail(mail_user, mailto_list, msg.as_string())
            s.close()
        except Exception as e:
            print(e)


