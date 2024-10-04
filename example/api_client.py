#!/usr/bin/python3

import sys

sys.path.append('../src')

import image_label_server.client as ilsc

BASE_URL = "http://127.0.0.1:44444"
USER_DATA = {"user":"fernando","password":"inmortal"}

# 
res_json = ilsc.get_size(BASE_URL, USER_DATA, "ber2024-body")
print(res_json)

#
res_img, res_json = ilsc.obtain_sample(BASE_URL, USER_DATA, "ber2024-body", 0)
print(res_json)
res_img.save('image.png')

# 
res_json["label"] = "neutro"
res_json = ilsc.classify_sample(BASE_URL, USER_DATA, res_json)
print(res_json)
