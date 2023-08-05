#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:23:40 2020

@author: sebastian
"""
import requests

req = requests.get("https://lg.govix.at/static")
req.raise_for_status()

data = req.text

output = []

for idx, line in enumerate(data.splitlines()):
    if idx == 0 or line.startswith(' '):
        continue
    else:
        netrange = line.split(' ')[0]
        output.append("""if source.ip << '%s' {
    add! extra.constituency = 'government'
}""" % netrange)

result = '\n'.join(output)
