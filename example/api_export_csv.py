#!/usr/bin/python3

import sys

sys.path.append('../src')

import image_label_server.export_csv as ilse


ilse.export_db_to_csv("~/.config/image-label-server/sqlite_dbs/ber2024-body.db", "some_name.csv")
