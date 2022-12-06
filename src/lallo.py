# coding: utf-8
import ntplib
import random
import datetime
ntp_pools=["0.it.pool.ntp.org","1.it.pool.ntp.org","2.it.pool.ntp.org","3.it.pool.ntp.org"]
print(str(datetime.datetime.fromtimestamp(ntplib.NTPClient().request(random.choice(ntp_pools)).tx_time)))
print(str(datetime.datetime.fromtimestamp(ntplib.NTPClient().request('ntp1.inrim.it',version=3).tx_time)))

