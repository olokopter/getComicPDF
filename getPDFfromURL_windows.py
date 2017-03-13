#!/usr/bin/env python
import urllib.request as urllib2
from bs4 import BeautifulSoup
from subprocess import call
import os
import shutil
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

comic_str= input("Provide input string after main adress:")
max_chapter= input("Provide max chapters: ")
#comic_str= "deadpools-art-of-war"
print ("Start to conv	ert all comics!")
for chapter in range(1,int(max_chapter)+1):
	os.makedirs(str(comic_str)+'_chapter_'+str(chapter))
	os.chdir(str(comic_str)+'_chapter_'+str(chapter))
	print ("Chapter: "+str(chapter))
	
	for page in range(1,100):
		try:
			print ("Start to get page "+str(page))
			req = urllib2.Request('http://www.readcomics.tv/'+str(comic_str)+'/chapter-'+str(chapter)+'/'+str(page), headers=hdr)
			page_html = urllib2.urlopen(req)
			html = page_html.read()

			soup = BeautifulSoup(html, 'html.parser')
			div_with_img_list = soup.find_all("div",class_="chapter-container")
			div_with_img = str(div_with_img_list[0])
			
			print ("Got page "+str(page))

			soup2 = BeautifulSoup(div_with_img, 'html.parser')
			img_url = soup2.find('img')['src']

			print ("Try to get img from url: "+str(img_url))
			req_img = urllib2.Request(img_url, headers=hdr)

			img_file = urllib2.urlopen(req_img)
			print ("Got img from url: "+str(img_url))
			
			output = open(comic_str+'_c'+str(chapter)+'_p'+str(page).zfill(4)+'.jpg','wb')
			print ("opened file")
			output.write(img_file.read())
			print ("write out file")
			output.close()
			
			
			print ("Saved page "+str(page)	)
		
		except:
			print ("Can not find URL "+str('http://hellocomic.com/'+str(comic_str)+'/c'+str(chapter)+'/p'+str(page)))
			print ("Probably max pages reached")
			break
	
	try:	
		call(["magick", "*.jpg", str(comic_str)+'_chapter_'+str(chapter)+".pdf"])
		os.rename(str(comic_str)+'_chapter_'+str(chapter)+".pdf", "../"+str(comic_str)+'_chapter_'+str(chapter)+".pdf")
		print ("Merged all pages from chapter: "+str(chapter)+" to "+str(comic_str)+'_chapter_'+str(chapter)+".pdf")
	except:
		print ("No images found in folder: "+str(comic_str)+'_chapter_'+str(chapter)+" deleting folder and go on with next chapter!")
	
	os.chdir("../")
	shutil.rmtree(str(comic_str)+'_chapter_'+str(chapter), ignore_errors=True)
	print ("All completed!")
