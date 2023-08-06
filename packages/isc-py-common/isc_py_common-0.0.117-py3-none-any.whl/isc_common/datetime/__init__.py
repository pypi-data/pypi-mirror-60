import datetime


def DateToStr(date, mask='%d.%m.%Y'):
    return datetime.datetime.strftime(date, mask)


def StrToDate(value_str, mask='%Y-%m-%dT%H:%M:%S'):
    value_str = str(value_str).split('.')[0]
    res = datetime.datetime.strptime(value_str, mask)
    return res + datetime.timedelta(hours=3)
