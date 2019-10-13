from re import sub
from unidecode import unidecode

def clean_string(s):
    if type(s)==str:
        s = unidecode(s)
        s = sub('[^A-Za-z0-9 ]+', '', s)
        s = sub('\s+', ' ', s)
        s = s.strip().title()
    else: s=''
    return s