What can you do in this package?
1. Use Google Translate to translate the text you want to translate. We support all languages supported by Google Translate, including automatic recognition.
2. Get the "tk" value of Google Translate. This "tk" value can be used for downloading Google Translate audio. (Note: Not all languages support voice, see https://translate.google.cn.)
3. Read the text you provided. Note: You must provide the source language.

How can I use these features?
1. translate text
    You can write codes like this:
    """
    >>> from GoogleTrans2020.Translator import translator as tr
    >>> tr(src="auto", dest="zh-CN").translate(text="Hello there!", multi=False, read=True, copy=True) 
    '你好'
    # "Src" is your translation source language, the default is "auto"; "dest" is your translation target language, the default is "zh-CN" (Simplified Chinese). "Text" is your translated text. "Multi" defaults to False. If True is entered, the data returned by Google server and then parsed by json will be returned. The "read" value defaults to True, which reads the text aloud, and false otherwise. The "copy" value defaults to False. True copies the translation result to the clipboard, and vice versa.
    """
2. Get "Tk" value
    You can write codes like this:
    """
    >>> from GoogleTrans2020.CalcTk import CalcTk as tk
    >>> tk().get_tk("Hello there!")
    '864133.761052'
    # It's very simple to use here! You just need to provide a string of text to the get_tk function to get the "tk" value.
    """

3. Read the text
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