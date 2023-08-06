from GoogleTrans2020.Translator import translator
from GoogleTrans2020.CalcTk import CalcTk
from pyperclip import copy
import argparse
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-s','-src','--source', default="auto", help="Enter the source language of the text.", type=str)
    argparser.add_argument('-d',"-dest","--destination", help="Enter the destination language.", type=str)
    argparser.add_argument('Words', help="Enter the text what you want to translate.", type=str)
    argparser.add_argument('-r','--read', help="Do you want to read the text?", action="store_true")
    argparser.add_argument('-c','--copy', help="Do you want to copy the text?", action="store_true")
    argparser.add_argument("-tk",'--get_tk_value', help = 'Get the "tk" value of the text.', action="store_true")
    argparser.add_argument("--copy_tk", help = 'Copy the "tk" value of the text.', action="store_true")
    args = argparser.parse_args()
    print(translator(src=args.source, dest=args.destination).translate(args.Words, read=args.read, copy=args.copy))
    if args.get_tk_value: print('tk = "{}"'.format(CalcTk().get_tk(args.Words)))
    if args.copy_tk: copy(CalcTk().get_tk(args.Words))
exit(main())