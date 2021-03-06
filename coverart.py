# liberally lifted/adapted from https://github.com/mobeets/cover-art

import os
import time
import glob
import urllib
import argparse
import unidecode
import webbrowser
import discogs_client

#DISCOGS_CONSUMER_KEY = os.environ['DISCOGS_CONSUMER_KEY']
#DISCOGS_CONSUMER_SECRET = os.environ['DISCOGS_CONSUMER_SECRET']

def save_image_album(im_url, d, outfile):
    headers = {
        'Accept-Encoding': 'gzip',
        'User-Agent': d.user_agent,
    }
    urllib.request.urlretrieve(im_url, outfile)
    # content, status_code = d._fetcher.fetch(d, 'GET', im_url, data=None, headers=headers)
    # if 200 <= status_code < 300:
    #     with open(outfile, 'w') as f:
    #         f.write(content)
    # else:
    #     1/0
    #     print "(I didn't save, but I may say I will.)", status_code

def save_image(im_url, d, outfile):
    if hasattr(d, 'user_agent'):
        return save_image_album(im_url, d, outfile)
    urlObj = urllib.request.urlopen(im_url)
    imageData = urlObj.read()
    urlObj.close()
    with open(outfile, 'wb') as f:
        f.write(imageData)

def make_filename(query):
    return query.replace('.', '_').replace('/', '_').replace(':', '-')

def get_im_url_album(d, query):
    for r in d.search(query): # had problems with adding type='title'
        if r.__class__.__name__ in ['Release', 'Master']:
            if r.images:
                return r.images[0]['uri']
            else:
                return None
            try:
                return r.images[0]['uri']
            except:
                try:
                    return r.master.images[0]['uri']
                except:
                    return r.thumb
            # if hasattr(r, 'images') and r.images:
            #     return r.images[0]['uri']
            # if hasattr(r, 'master'):
            #     if hasattr(r.master, 'images') and r.master.images:
            #         return r.master.images[0]['uri']
            # if hasattr(r, 'thumb'):
            #     return r.thumb
    return None

def already_exists(query, outdir):
    return any([os.path.splitext(x)[0] == query for x in os.listdir(outdir)])

def find_and_download_image(d, query, outname, outdir, kind):
    im_url = get_im_url_album(d, query)

    if im_url is None or (type(im_url) is list and len(im_url) == 0):
        print(query)
        print('    NOT FOUND')
        return
    ext = os.path.splitext(im_url)[1]
    ext = ext.replace('jpg', 'jpeg')
    # ext = '.png'
    outfile = os.path.join(outdir, outname + ext)
    save_image(im_url, d, outfile)
    # print(query)
    print('Saved {0}'.format(outfile))

def get_album_info(line):
    ps = line.split("'s")
    artist = ps[0].strip()
    album = ps[1].strip()
    album, year = album.split(' (')
    year = year.replace(')', '').strip()
    album = album.strip()
    return artist, album, year

def print_info(d, query, kind, i):
    if kind == "film":
        info = get_film_info(d, query)
    elif kind == "album":
        info = get_album_info(query)
    elif kind == "book":
        info = get_book_info(query)
    if len(info) == 3:
        print("""-    \n    pos: {}\n    artist: "{}"\n    album: "{}"\n    year: {}""".format(i+1, info[0], info[1].replace('"',''), info[2]))

def dicogs_auth(verifier=None):
    d = discogs_client.Client('ExampleApplication/0.1')
    d.set_consumer_key(DISCOGS_CONSUMER_KEY, DISCOGS_CONSUMER_SECRET)
    request_token, request_secret, url = d.get_authorize_url()
    if not verifier:
        print(url)
        if raw_input('Go to this url? ').strip().lower() != 'n':
            webbrowser.open_new_tab(url)
        else:
            return None
        verifier = raw_input('Gimme that verification code: ').strip()
    access_token, access_secret = d.get_access_token(verifier)
    me = d.identity()
    return d

MIN_LENGTH = 3 # was at 6?
def parse(content):
    lines = []
    for line in content.split('\n'):
        if line.startswith('    '): # skip comments on albums
            continue
        line = line.strip()
        if not line.startswith('#') and len(line) >= MIN_LENGTH: # skip headers
            lines.append(line)
    return lines

# def load(infile):
#     with open(infile) as f:
#         out = unidecode.unidecode(f.read())
#         return out.split('-----')[0] # keep everything before -----

def main(infile, outdir):
    d = discogs_client.Client('ExampleApplication/0.1', user_token="VzzJJATOLvHNkPbxLNkMhAasGDUXKscYoWfgzUnV")
    kind="album"
    get_info=False

    # lines = parse(load(infile))
    #for i, line in enumerate(infile):
    for i, line in enumerate(infile):
        query = line
        if get_info and d is not None:
            print_info(d, line, kind, i)
            continue
        outname = make_filename(query)
        if already_exists(outname, outdir):
            pass
        elif d is None:
            print(outname)
        else:
            find_and_download_image(d, query, outname, outdir, kind)
            # try:
            #     find_and_download_image(d, query, outname, outdir, kind)
            # except Exception, e:
            #     print query
            #     print e.__str__()
            #     print '    BUGGIN OUT - might work next time'
            #     time.sleep(2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='infile or indir')
    parser.add_argument('-o', type=str, help='outdir')
    parser.add_argument('--type', type=str, default="album", choices=("album", "film", "book"), help='type of image to search for')
    parser.add_argument('--get_info', action='store_true', help='print info (no images saved)')
    parser.add_argument('-c', action='store_true', default=False, help='check images remaining')
    parser.add_argument('--all', action='store_true', default=False, help='download all')
    args = parser.parse_args()
    infile = os.path.abspath(args.i)
    if not args.get_info:
        outdir = os.path.abspath(args.o)
        if not args.all and not os.path.exists(outdir):
            os.mkdir(outdir)
    else:
        outdir = None

    # d = dicogs_auth()
    # n.b. personal access token is from https://www.discogs.com/settings/developers
    d = discogs_client.Client('ExampleApplication/0.1', user_token="VzzJJATOLvHNkPbxLNkMhAasGDUXKscYoWfgzUnV")

    main(infile, outdir, d, args.type, args.get_info)