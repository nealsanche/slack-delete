from urllib.parse import urlencode
from urllib.request import urlopen
import time
import json
import codecs
import datetime
from collections import OrderedDict

reader = codecs.getreader("utf-8")

# Obtain here: https://api.slack.com/custom-integrations/legacy-tokens
token = ''

# Params for file listing. More info here: https://api.slack.com/methods/files.list

# Delete files older than this:
days = 140
ts_to = int(time.time()) - days * 24 * 60 * 60

# How many? (Maximum is 1000, otherwise it defaults to 100)
count = 1000

# Types?
types = 'all'
# types = 'spaces,snippets,images,gdocs,zips,pdfs'
# types = 'zips'


def list_files():
    params = {
        'token': token,
        'ts_to': ts_to,
        'count': count,
        'types': types
    }
    uri = 'https://slack.com/api/files.list'
    response = reader(urlopen(uri + '?' + urlencode(params)))

    json_text = json.load(response)

    paging = json_text['paging']
    pages = paging["pages"]
    files = json_text['files']

    print("Pages = {pages}".format(**locals()))

    for i in range(2,pages+2):
        params = {
            'token': token,
            'ts_to': ts_to,
            'count': count,
            'types': types,
            'page': i
        }
        print(i)
        uri = 'https://slack.com/api/files.list'
        response = reader(urlopen(uri + "?" + urlencode(params)))
        morefiles = json.load(response)['files']
        files.extend(morefiles)

    return files


def filter_by_size(files, mb, greater_or_smaller):
    if greater_or_smaller == 'greater':
        return [file for file in files if (file['size'] / 1000000) > mb]
    elif greater_or_smaller == 'smaller':
        return [file for file in files if (file['size'] / 1000000) < mb]
    else:
        return None


def filter_by_name(files, prefix):
    return [file for file in files if file['name'].lower().startswith(prefix)]

def filter_by_user(files, uid):
    return [file for file in files if file['user'].startswith(uid)]

def info(file):
    order = ['Title', 'Name', 'Created', 'Size', 'Filetype',
             'Comment', 'Permalink', 'Download', 'User', 'Channels']
    info = {
        'Title': file['title'],
        'Name': file['name'],
        'Created': datetime.datetime.utcfromtimestamp(file['created']).strftime('%B %d, %Y %H:%M:%S'),
        'Size': str(file['size'] / 1000000) + ' MB',
        'Filetype': file['filetype'],
        'Comment': file['initial_comment'] if 'initial_comment' in file else '',
        'Permalink': file['permalink'],
        'Download': file['url_private'],
        'User': file['user'],
        'Channels': file['channels']
    }
    return OrderedDict((key, info[key]) for key in order)


def file_ids(files):
    return [f['id'] for f in files]


def delete_files(file_ids):
    num_files = len(file_ids)
    for index, file_id in enumerate(file_ids):
        params = {
            'token': token,
            'file': file_id
        }
        uri = 'https://slack.com/api/files.delete'
        response = reader(urlopen(uri + '?' + urlencode(params)))
        print((index + 1, "of", num_files, "-",
               file_id, json.load(response)['ok']))
        time.sleep(2)

def delete_by_user(files, uid):
    files_by_user = filter_by_user(files, uid)
    print(len(files_by_user))
    [print(file['name']) for file in files_by_user]
    [info(file) for file in files_by_user]
    ids = file_ids(files_by_user)
    delete_files(ids)

def delete_by_prefix(files, prefix):
    files_by_name = filter_by_name(files, prefix)
    print(len(files_by_name))
    [print(file['name']) for file in files_by_name]
    [info(file) for file in files_by_name]
    ids = file_ids(files_by_name)
    delete_files(ids)

files = list_files()
print(len(files))
delete_by_prefix(files, 'screenshot')
delete_by_prefix(files, 'slack for ios')
delete_by_prefix(files, 'screen shot')
delete_by_prefix(files, '2014')
delete_by_prefix(files, '2015')
delete_by_prefix(files, '2016')
delete_by_prefix(files, '2017')
delete_by_prefix(files, "img_")
delete_by_prefix(files, "imag")
delete_by_prefix(files, "img-")
delete_by_prefix(files, "vid_")
delete_by_prefix(files, "image uploaded from ios")
delete_by_prefix(files, "pasted image at")
delete_by_prefix(files, "download_")
delete_by_prefix(files, "capture")
delete_by_prefix(files, "image")
delete_by_prefix(files, "tempfileforshare")
delete_by_prefix(files, "downtown p7 p8 report")
delete_by_prefix(files, "portal_")
delete_by_prefix(files, "profile_")
delete_by_prefix(files, "medal_")
delete_by_prefix(files, "levelup_")
delete_by_prefix(files, "ingress_")
delete_by_prefix(files, "mms_img")
delete_by_prefix(files, "quickmemo")
delete_by_prefix(files, "pokémon go")

delete_by_user(files, "U02H7BFAA") # Owainsky
delete_by_user(files, "U02HJTXNC") # Elevenrum
delete_by_user(files, "U02H7FRAZ") # Indepth
delete_by_user(files, "U02GYD4BH") # Uberuser
delete_by_user(files, "U02H1EULL") # aaralyn
delete_by_user(files, "U02HRS3Q0") # spotooky
delete_by_user(files, "U03RZ4T9V") # pipdaship

[print(file['name']) for file in sorted(files, key=lambda fi: fi['name'])]
