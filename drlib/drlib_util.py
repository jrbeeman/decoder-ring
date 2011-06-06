from BeautifulSoup import BeautifulSoup, SoupStrainer
import re, pprint, csv, sys, unicodedata, time, htmlentitydefs
import mechanize, urllib, urllib2, urlparse
import os, errno, hashlib


# Recursively and gracefully create a directory
def mkdir_p(path):
    # Try to make the files destination
    try:
        os.makedirs(path)
    except OSError, exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


# Clean a string, converting from Unicode to ASCII, and removing some special characters
def cleanString(text):
    # Convert Unicode to ASCII
    if (isinstance(text, unicode)):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')

    isNumeric = False
    if (isinstance(text, int)):
        isNumeric = True

    text = str(text)
    text = text.replace("\n", ' ')
    text = text.replace("&nbsp;", ' ')
    text = text.strip()

    if (isNumeric):
        text = int(text)

    return text


# Get a URL, but do so from a cache if possible. If not, get it and cache it
def cacheHTML(browser, url, cachepath = ''):
    print "Fetching: " + url
    m = hashlib.md5()
    m.update(url)
    if (cachepath):
        dest = cachepath + m.hexdigest() + '.html'
    else:
        dest = '/Users/jbeeman/tmp/dr-import-cache/' + m.hexdigest() + '.html'
    if (os.path.exists(dest)):
        print '...Using local cache'
        file = open(dest)
        markup = file.read()
        markup = markup.replace('<style type=."', '<style type="')
        markup = markup.replace('"; onmouseout="', ';" onmouseout="')
    else:
        # Wait a second so we don't hammer the site
        print 'Waiting...'
        time.sleep(2)
        response = browser.open(url)
        markup = response.read()
        # Cleanup
        markup = markup.replace('<style type=."', '<style type="')
        markup = markup.replace('"; onmouseout="', ';" onmouseout="')
        # Save the markup locally
        file = open(dest, 'wb')
        file.write(markup)
        file.close()
        print '...Saved local cache: ' + dest

    return markup

# Download a file (like an image) to a local cache and return its filename
def cacheRemoteFile(url, cachepath = ''):
    # Make sure it's a valid URL
    l = urlparse.urlparse(url)
    if (l[0] == '' or l[0] == 'c'):
        return ''

    extension = ''
    hasExtension = re.compile('''(.jpg|.gif|.png)$''').search(url)
    if (hasExtension):
        extension = hasExtension.group(1)

    m = hashlib.md5()
    m.update(url)
    newFile = m.hexdigest() + extension

    # Do we already have the avatar
    if (cachepath):
        dest = cachepath + newFile
    else:
        dest = '/Users/jbeeman/tmp/dr-import-cache/' + newFile

    if (os.path.exists(dest) != True):
        # Figure out where we put the file and make sure the directory exists
        destpwd = os.path.dirname(dest)
        mkdir_p(destpwd)
        # Download and write the file
        print "Downloading file: " + url
        try:
            file = urllib2.urlopen(url).read()
        except urllib2.HTTPError, image:
            file = ''
        except urllib2.URLError, image:
            file = ''
        output = open(dest, 'wb')
        output.write(file)
        output.close()

    return newFile

def writeCSV(fieldnames, data, destFile):
    print "Writing " + str(len(data)) + " rows to " + destFile
    f = open(destFile, 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    headers = dict( (n,n) for n in fieldnames )
    writer.writerow(headers)
    for guid, item in data.items():
        writer.writerow(item)
    f.close()

