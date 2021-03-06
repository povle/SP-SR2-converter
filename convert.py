#!/usr/bin/env python3
import argparse
import io
import os.path
import shutil
import requests
from convert_file import convert_file

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('id', nargs='?', help='ID of the craft (https://www.simpleplanes.com/a/??????/)')
group.add_argument('--input_file', '-i', type=argparse.FileType('rb'), help='path to the source craft xml')
parser.add_argument('--scale', '-s', type=float, default=1, help='scale of the converted craft')
parser.add_argument('--output_file', '-o', type=argparse.FileType('wb'), help='path to the output file')
group2 = parser.add_mutually_exclusive_group()
group2.add_argument('--only_ids', nargs='*', metavar='part_id', help='convert only parts with given ids')
group2.add_argument('--exclude_ids', nargs='*', metavar='part_id', default=[], help='ignore parts with given ids')
group3 = parser.add_mutually_exclusive_group()
group3.add_argument('--only_types', nargs='*', metavar='SP_type', help='convert only parts with given types')
group3.add_argument('--exclude_types', nargs='*', metavar='SP_type', default=[], help='ignore parts with given types')
args = parser.parse_args()

output_file = args.output_file or None
if args.id:
    r = requests.get(f'http://www.simpleplanes.com/Client/DownloadAircraft?a={args.id}')
    if r.content == b'0':
        raise ValueError('Incorrect craft ID')
    input_file = io.BytesIO(r.content)
    if output_file is None:
        output_file = open(args.id+'_SR.xml', 'wb')
else:
    input_file = args.input_file
    if output_file is None:
        output_name = os.path.split(input_file.name)[1]
        output_name = os.path.splitext(output_name)[0]+'_SR.xml'
        output_file = open(output_name, 'wb')

with input_file as i, output_file as o:
    converted = convert_file(i, args)
    shutil.copyfileobj(converted, o)
