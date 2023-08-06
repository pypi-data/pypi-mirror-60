## -*- coding: utf-8 -*-
import requests, execjs, json, sys
from GoogleTrans2020.CalcTk import CalcTk
import time
from playsound import playsound as read_text
from os import remove as delete
from pyperclip import copy as copyx

class translator():
    support_lauguage = {'检测语言': 'auto', 
                        '阿尔巴尼亚语': 'sq', 
                        '阿拉伯语': 'ar', 
                        '阿姆哈拉语': 'am', 
                        '阿塞拜疆语': 'az', 
                        '爱尔兰语': 'ga', 
                        '爱沙尼亚语': 'et', 
                        '巴斯克语': 'eu', 
                        '白俄罗斯语': 'be', 
                        '保加利亚语': 'bg', 
                        '冰岛语': 'is', 
                        '波兰语': 'pl', 
                        '波斯尼亚语': 'bs', 
                        '波斯语': 'fa', 
                        '布尔语(南非荷兰语)': 'af', 
                        '丹麦语': 'da', 
                        '德语': 'de', 
                        '俄语': 'ru', 
                        '法语': 'fr', 
                        '菲律宾语': 'tl', 
                        '芬兰语': 'fi', 
                        '弗里西语': 'fy', 
                        '高棉语': 'km', 
                        '格鲁吉亚语': 'ka', 
                        '古吉拉特语': 'gu', 
                        '哈萨克语': 'kk', 
                        '海地克里奥尔语': 'ht', 
                        '韩语': 'ko', 
                        '豪萨语': 'ha', 
                        '荷兰语': 'nl', 
                        '吉尔吉斯语': 'ky', 
                        '加利西亚语': 'gl', 
                        '加泰罗尼亚语': 'ca', 
                        '捷克语': 'cs', 
                        '卡纳达语': 'kn', 
                        '科西嘉语': 'co', 
                        '克罗地亚语': 'hr', 
                        '库尔德语': 'ku', 
                        '拉丁语': 'la', 
                        '拉脱维亚语': 'lv', 
                        '老挝语': 'lo', 
                        '立陶宛语': 'lt', 
                        '卢森堡语': 'lb', 
                        '罗马尼亚语': 'ro', 
                        '马尔加什语': 'mg', 
                        '马耳他语': 'mt', 
                        '马拉地语': 'mr', 
                        '马拉雅拉姆语': 'ml', 
                        '马来语': 'ms', 
                        '马其顿语': 'mk', 
                        '毛利语': 'mi', 
                        '蒙古语': 'mn', 
                        '孟加拉语': 'bn', 
                        '缅甸语': 'my', 
                        '苗语': 'hmn', 
                        '南非科萨语': 'xh', 
                        '南非祖鲁语': 'zu', 
                        '尼泊尔语': 'ne', 
                        '挪威语': 'no', 
                        '旁遮普语': 'pa', 
                        '葡萄牙语': 'pt', 
                        '普什图语': 'ps', 
                        '齐切瓦语': 'ny', 
                        '日语': 'ja', 
                        '瑞典语': 'sv', 
                        '萨摩亚语': 'sm', 
                        '塞尔维亚语': 'sr', 
                        '塞索托语': 'st', 
                        '僧伽罗语': 'si', 
                        '世界语': 'eo', 
                        '斯洛伐克语': 'sk', 
                        '斯洛文尼亚语': 'sl', 
                        '斯瓦希里语': 'sw', 
                        '苏格兰盖尔语': 'gd', 
                        '宿务语': 'ceb', 
                        '索马里语': 'so', 
                        '塔吉克语': 'tg', 
                        '泰卢固语': 'te', 
                        '泰米尔语': 'ta', 
                        '泰语': 'th', 
                        '土耳其语': 'tr', 
                        '威尔士语': 'cy', 
                        '乌尔都语': 'ur', 
                        '乌克兰语': 'uk', 
                        '乌兹别克语': 'uz', 
                        '西班牙语': 'es', 
                        '希伯来语': 'iw', 
                        '希腊语': 'el', 
                        '夏威夷语': 'haw', 
                        '信德语': 'sd', 
                        '匈牙利语': 'hu', 
                        '修纳语': 'sn', 
                        '亚美尼亚语': 'hy', 
                        '伊博语': 'ig', 
                        '意大利语': 'it', 
                        '意第绪语': 'yi', 
                        '印地语': 'hi', 
                        '印尼巽他语': 'su', 
                        '印尼语': 'id', 
                        '印尼爪哇语': 'jw', 
                        '英语': 'en', 
                        '约鲁巴语': 'yo', 
                        '越南语': 'vi', 
                        '中文(繁体)': 'zh-TW', 
                        '中文(简体)': 'zh-CN'}

    headers = {
        'Host': 'translate.google.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/2010'
                      '0101 Firefox/50.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': 'https://translate.google.cn/',
        'Cookie': 'NID=101=pkAnwSBvDm2ACj2lEVnWO7YEPUoWCTges7B7z2jJNyrNwAZ2OL9F'
                   'FOQLpdethA_20gCVqukiHnVm1hUbMGZc_ItQFdP5AHoq5XoMeEORaeidU19'
                   '6NDVRsrAu_zT0Yfsd; _ga=GA1.3.1338395464.1492313906',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0'
    }
    
    def __init__(self, src='auto', dest='en', updata_time=600):
        if src not in self.support_lauguage and src not in self.support_lauguage.values():
            raise ValueError('source language not support')
        if dest not in self.support_lauguage and dest not in self.support_lauguage.values():
            raise ValueError('destination language not support')
        self.url = 'https://translate.google.cn/translate_a/single'
        self.params = {
            'client': 't',
            'sl': src,
            'tl': dest,
            'hl': 'zh-CN',
            'dt': 'at', 'dt': 'bd',
            'dt': 'ex', 'dt': 'ld', 'dt': 'md',
            'dt': 'qca', 'dt': 'rw', 'dt': 'rm', 'dt': 'ss', 'dt': 't',
            'ie': 'UTF-8', 'oe': 'UTF-8', 'source': 'bh', 'ssel': '0',
            'tsel': '0', 'kc': '1', 'tk': '376032.257956'
        }
        self.updata_time = updata_time
        self.__updata_tk()
        self.dest = dest

    def translate(self, text, multi=False, read=True, copy=False):
        if time.time() > self.__next_up_time:
            self.__updata_tk()
        data = {'q': text}
        self.params['tk'] = self.__TK.get_tk(text)
        res = self.__get_res(data)
        ret_list = json.loads(res.text)
        if copy:
            copyx(ret_list[0][0][0])
        if read:
            self.read_trans_text(ret_list[0][0][0])
            return (ret_list[0][0][0])
        if multi:
            return ret_list
        if not read and not multi:
            return (ret_list[0][0][0])


    def __updata_tk(self):
        self.__TK = CalcTk()
        self.__next_up_time = time.time() + self.updata_time

    def __get_res(self, data):
        res = requests.post(self.url,
                            headers=self.headers,
                            data=data,
                            params=self.params,
                            timeout=6)
        res.raise_for_status()
        return res
    
    def read_trans_text(self, text):
        audio = requests.get("https://translate.google.cn/translate_tts", 
                            params = {"q": text,
                                    "tl": self.dest,
                                    "tk": CalcTk().get_tk(text),
                                    "client":"webapp"},
                            headers = self.headers)
        mp3_name = "translate_tts.mp3"
        music = open(mp3_name, "wb")
        music.write(audio.content)
        music.close()
        read_text(mp3_name)       
        delete(mp3_name)