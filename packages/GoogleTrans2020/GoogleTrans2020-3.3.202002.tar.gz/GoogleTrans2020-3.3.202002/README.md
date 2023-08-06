What can you do in this package?
1. See what languages do we support.
2. Use Google Translate to translate the text you want to translate. We support all languages supported by Google Translate, including automatic recognition.
3. Get the "tk" value of Google Translate. This "tk" value can be used for downloading Google Translate audio. (Note: Not all languages support voice, see https://translate.google.cn.)
4. Read the text you provided. Note: You must provide the source language.

How can I use these features?
1. See what languages do we support
    You should write codes like this:
    """
    >>> from GoogleTrans2020.Translator import support_languanges as sl
    >>> sl()
    ['检测语言', '阿尔巴尼亚语', '阿拉伯语', '阿姆哈拉语', '阿塞拜疆语', '爱尔兰语', '爱沙尼亚语', '巴斯克语', '白俄罗斯语', '保加利亚语', '冰岛语', '波兰语', '波斯尼亚语', '波斯语', '布尔语(南非荷兰语)', '丹麦语', '德语', '俄语', '法语', '菲律宾语', '芬兰语', '弗里西语', '高棉语', '格鲁吉亚语', '古吉拉特语', '哈萨克语', '海地克里奥尔语', '韩语', '豪萨语', '荷兰语', '吉尔吉斯语', '加利西亚语', '加泰罗尼亚语', '捷克语', '卡纳达语', '科西嘉语', '克罗地亚语', '库尔德语', '拉丁语', '拉脱维亚语', '老挝语', '立陶宛语', '卢森堡语', '罗马尼亚语', '马尔加什语', '马耳他语', '马拉地语', '马拉雅拉姆语', '马来语', '马其顿语', '毛利语', '蒙古语', '孟加拉语', '缅甸语', '苗语', '南非科萨语', '南非祖鲁语', '尼泊尔语', '挪威语', '旁遮普语', '葡萄牙语', '普什图语', '齐切瓦语', '日语', '瑞典语', '萨摩亚语', '塞尔维亚语', '塞索托语', '僧伽罗语', '世界语', '斯洛伐克语', '斯洛文尼亚语', '斯瓦希里语', '苏格兰盖尔语', '宿务语', '索马里语', '塔吉克语', '泰卢固语', '泰米尔语', '泰语', '土耳其语', '威尔士语', '乌尔都语', '乌克兰语', '乌兹别克语', '西班牙语', '希伯来语', '希腊语', '夏威夷语', '信德语', '匈牙利语', '修纳语', '亚美尼亚语', '伊博语', '意大利语', '意第绪语', '印地语', '印尼巽他语', '印尼语', '印尼爪哇语', '英语', '约鲁巴语', '越南语', '中文(繁体)', '中文(简体)']
    >>> sl(1,0)
    '我们支持的语言有：阿尔巴尼亚语、阿拉伯语、阿姆哈拉语、阿塞拜疆语、爱尔兰语、爱沙尼亚语、巴斯克语、白俄罗斯语、保加利亚语、冰岛语、波兰语、波斯尼亚语、波斯语、布尔语(南非荷兰语)、丹麦语、德语、俄语、法语、菲律宾语、芬兰语、弗里西语、高棉语、格鲁吉亚语、古吉拉特语、哈萨克语、海地克里奥尔语、韩语、豪萨语、荷兰语、吉尔吉斯语、加利西亚语、加泰罗尼亚语、捷克语、卡纳达语、科西嘉语、克罗地亚语、库尔德语、拉丁语、拉脱维亚语、老挝语、立陶宛语、卢森堡语、罗马尼亚语、马尔加什语、马耳他语、马拉地语、马拉雅拉姆语、马来语、马其顿语、毛利语、蒙古语、孟加拉语、缅甸语、苗语、南非科萨语、南非祖鲁语、尼泊尔语、挪威语、旁遮普语、葡萄牙语、普什图语、齐切瓦语、日语、瑞典语、萨摩亚语、塞尔维亚语、塞索托语、僧伽罗语、世界语、斯洛伐克语、斯洛文尼亚语、斯瓦希里语、苏格兰盖尔语、宿务语、索马里语、塔吉克语、泰卢固语、泰米尔语、泰语、土耳其语、威尔士语、乌尔都语、乌克兰语、乌兹别克语、西班牙语、希伯来语、希腊语、夏威夷语、信德语、匈牙利语、修纳语、亚美尼亚语、伊博语、意大利语、意第绪语、印地语、印尼巽他语、印尼语、印尼爪哇语、英语、约鲁巴语、越南语、中文(繁体)、中文(简体)。'
    >>> sl(0,1)
    ['auto', 'sq', 'ar', 'am', 'az', 'ga', 'et', 'eu', 'be', 'bg', 'is', 'pl', 'bs', 'fa', 'af', 'da', 'de', 'ru', 'fr', 'tl', 'fi', 'fy', 'km', 'ka', 'gu', 'kk', 'ht', 'ko', 'ha', 'nl', 'ky', 'gl', 'ca', 'cs', 'kn', 'co', 'hr', 'ku', 'la', 'lv', 'lo', 'lt', 'lb', 'ro', 'mg', 'mt', 'mr', 'ml', 'ms', 'mk', 'mi', 'mn', 'bn', 'my', 'hmn', 'xh', 'zu', 'ne', 'no', 'pa', 'pt', 'ps', 'ny', 'ja', 'sv', 'sm', 'sr', 'st', 'si', 'eo', 'sk', 'sl', 'sw', 'gd', 'ceb', 'so', 'tg', 'te', 'ta', 'th', 'tr', 'cy', 'ur', 'uk', 'uz', 'es', 'iw', 'el', 'haw', 'sd', 'hu', 'sn', 'hy', 'ig', 'it', 'yi', 'hi', 'su', 'id', 'jw', 'en', 'yo', 'vi', 'zh-TW', 'zh-CN']

2. Translate text
    You can write codes like this:
    """
    >>> from GoogleTrans2020.Translator import translator as tr
    >>> tr(src="auto", dest="zh-CN").translate(text="Hello there!", multi=False, read=True, copy=True) 
    '你好'
    # "Src" is your translation source language, the default is "auto"; "dest" is your translation target language, the default is "zh-CN" (Simplified Chinese). "Text" is your translated text. "Multi" defaults to False. If True is entered, the data returned by Google server and then parsed by json will be returned. The "read" value defaults to True, which reads the text aloud, and false otherwise. The "copy" value defaults to False. True copies the translation result to the clipboard, and vice versa.
    """
3. Get "Tk" value
    You can write codes like this:
    """
    >>> from GoogleTrans2020.CalcTk import CalcTk as tk
    >>> tk().get_tk("Hello there!")
    '864133.761052'
    # It's very simple to use here! You just need to provide a string of text to the get_tk function to get the "tk" value.
    """

4. Read the text
    You can write codes like this:
    """
    >>> from GoogleTrans2020.Tranlator import translator
    >>> translator().read_trans_text("The quick brown fox jumps over the lazy dog.")
    (It will read this sentence.)
    # It is also easy to use! "read_trans_text" only have one parameter - "text".

What languages does this package have?

Albanian, Arabic, Amharic, Azerbaijani, Irish, Estonian, Basque, Belarusian, Bulgarian, Icelandic, Polish, Bosnian, Persian, Boer (Afrikaans) , Danish, German, Russian, French, Filipino, Finnish, Frisian, Khmer, Georgian, Gujarati, Kazakh, Haitian Creole, Korean, Hausa, Dutch, Kyrgyz, Galician, Catalan, Czech, Kannada, Corsican, Croatian, Kurdish, Latin, Latvian, Lao, Lithuanian, Luxembourg Language, Romanian, Malagasy, Maltese, Marathi, Malayalam, Malay, Macedonian, Maori, Mongolian, Bengali, Burmese, Hmong, Xhosa English, Afrikaans Zulu, Nepali, Norwegian, Punjabi, Portuguese, Pashto, Tsichewa, Japanese, Swedish, Samoa, Serbian, Serbian Sotho, Sinhala, Esperanto, Slovak, Slovenian, Swahili, Scottish Gaelic, Cebu, Somali, Tajik, Telugu, Tamil, Thai, Turkish Language, Welsh, Urdu, Ukrainian, Uzbek, Spanish, Hebrew, Greek, Hawaiian, Sindhi, Hungarian, Shona, Armenian, Igbo, Italian, Yiddish, Hindi, Indonesian Sundanese, Indonesian, Indonesian Javanese, English, Yoruba, Vietnamese, Chinese (Traditional), Chinese (Simplified)

At last:
Acknowledgements:
1. Microsoft
2. GitHub
3. pyperclip
4. PyExecJs
5. playsound
6. requests
7. GoogleFreeTans
8. Python
...
Thanks for you!