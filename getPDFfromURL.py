#!/usr/bin/env python
import os
import platform
# import shutil

try:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen
from subprocess import call
from threading import Thread

from bs4 import BeautifulSoup
import glob

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}
COMIC_PAGE = 'http://www.readcomics.tv'
PDF = True


def get_input(question):
    """Request user input, python2/3 safe."""
    try:
        return raw_input(question)
    except NameError:
        return input(question)


def get_url(url):
    """Get contents of requested url."""
    print(url)
    req = Request(url, headers=HEADER)
    return urlopen(req).read()


def get_chapter_list(url):
    """Get list of chapters by searching overview page."""
    soup = BeautifulSoup(get_url(url), 'html.parser')
    for basic_list in soup.find_all('ul', class_='basic-list'):
        a_list = basic_list.find_all('a', class_='ch-name')
        if len(a_list) > 0:
            return [
                (int(a['href'].split('-')[-1]), a['href'])
                for a in a_list
            ]


def get_image_list(url):
    """Get image list using url of first picture and count of pages."""
    soup = BeautifulSoup(get_url(url), 'html.parser')

    num_pages = int(soup.find('div', class_='ct-right')
                        .find('table', class_='full-table')
                        .find('div', class_='label')
                        .text.strip(' of'))
    img_url = soup.find('div', class_='chapter-container').find('img')['src']

    return [
        (i, img_url.replace('1.jpg', '{}.jpg'.format(i)))
        for i in range(1, num_pages + 1)
    ]


def get_folder(comic_str, chapter_num):
    """Return folder path."""
    return os.path.join('.', comic_str, '{:03d}'.format(chapter_num))


def create_folder(comic_str, chapter_num):
    """Create folder, if nessecary."""
    folder = get_folder(comic_str, chapter_num)
    try:
        os.makedirs(folder)
    except os.error:
        pass
    return folder


def download_images(img_list, save_path):
    """Download images."""
    for img_num, img_url in img_list:
        img_file = get_url(img_url)
        with open(os.path.join(save_path, '{:04d}.jpg'.format(img_num)), 'wb') as output:
            output.write(img_file)


def create_pdf(folder, chapter_num):
    """Create pdf using magick on Windows and convert on else."""
    images_path = os.path.join(folder, '*.jpg')
    pdf_path = os.path.join(folder, 'chapter_{:03d}.pdf'.format(chapter_num))
    
    if platform.system() == 'Windows':
        toolname = 'magick'
    else:
        toolname = 'convert'
    print(toolname+" "+str(images_path)+" "+pdf_path)
    call([toolname, images_path, pdf_path])

def clean_jpg(folder):
    images_path = os.path.join(folder, '*.jpg')
    listWithjpgFiles = glob.glob(images_path)
    for jpgFile in listWithjpgFiles:
        os.remove(jpgFile)
    
def main():
    comic_str = get_input('Provide input string after main adress: ')
    numSpChapter_str = get_input('Give number of chapter that you want to dl (if blank all are loaded): ')
    url = COMIC_PAGE+'/comic/'+comic_str+"/"
    threadlist = []
    numSpChapter=-1
    print("Running on",platform.system())
    if  numSpChapter_str:
        try:
           numSpChapter = int(numSpChapter_str)
        except ValueError:
           print("Please provide int chapter!")
           exit(1)
    print('Getting chapter list')
    chapter_list = get_chapter_list(url)
    print('Downloading images')
    for chapter_num, chapter_url in chapter_list:
        if numSpChapter!=-1:
            if numSpChapter != chapter_num:
                continue
        folder = create_folder(comic_str, chapter_num)
        img_list = get_image_list(chapter_url)
        thread = Thread(target=download_images, args=(img_list, folder))
        thread.start()
        threadlist.append(thread)

    for thread in threadlist:
        thread.join()

    if PDF:
        for chapter_num, _ in chapter_list:
            if numSpChapter!=-1:
                if numSpChapter != chapter_num:
                    continue
            print('Creating pdf file for chapter {}'.format(chapter_num))
            create_pdf(get_folder(comic_str, chapter_num), chapter_num)
            clean_jpg(get_folder(comic_str, chapter_num))
    print('All completed!')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Download canceled!')
