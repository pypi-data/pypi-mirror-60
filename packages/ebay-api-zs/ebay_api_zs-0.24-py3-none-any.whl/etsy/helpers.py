from datetime import datetime


def tsz_to_datetime(tsz, to_str=False, isoformat=False):
    dtm = datetime.utcfromtimestamp(tsz)
    if to_str:
        if isoformat:
            dtm = dtm.isoformat()
        else:
            dtm = dtm.strftime("%Y-%m-%d %H:%M:%S")
    return dtm
