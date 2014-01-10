#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import urllib
import urllib2
import os
from glob import glob
from sys import platform as _platform
import locale

# Some globals
HOME_PATH = os.path.expanduser("~")
BASE_PATH = os.path.join(HOME_PATH, '.bingwallpaper')  # where to save
LOCAL = locale.getdefaultlocale()[0].replace('_', '-', 1)  # local string identifier ("fr-FR" for instance)

_BASE_JSON_BING_WALLPAPER_URL = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx={}&n=1&mkt={}'  # the json ress to parse


if _platform == "win32":  # windows stuff
	import ctypes

	def get_screen_size():
		'''
		get screen pixel resolution using ctype
		'''
		user32 = ctypes.windll.user32
		return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

	def cleanup_old_bmp():
		'''
		delete all bmp images (larger size than jpg ones)
		'''
		for filepath in glob(os.path.join(BASE_PATH, "*.bmp")):
			try:
				os.remove(filepath)
			except OSError:
				pass

	def set_background_wallpaper(path):
		cleanup_old_bmp()

		#convert to BMP
		from PIL import Image
		newpath = path.replace('jpg', 'bmp', 1)
		Image.open(path).save(newpath)
		#set
		ctypes.windll.user32.SystemParametersInfoA(20, 0, newpath, 0)
else:  # assume gnome stuff
	import Tkinter
	import gconf

	def get_screen_size():
		'''
		get screen pixel resolution using tkinter
		'''
		root = Tkinter.Tk()
		return root.winfo_screenwidth(), root.winfo_screenheight()

	def set_background_wallpaper(path):
		conf = gconf.client_get_default()
		conf.set_string('/desktop/gnome/background/picture_filename', os.path.abspath(path))


def get_formated_screen_size():
	'''
	formated screen size like "1950*1080".
	'''
	return "%ix%i" % get_screen_size()


class BingWallpaper(object):
	'''
	Allow to parse and download latest bing wallpaper according to the screen resolution and local lang.
	'''
	def __init__(self, id=0, lang=LOCAL):
		self._id = id
		self._lang = lang
		self._jsondata = None

	@property
	def jsondata(self):
		if self._jsondata is None:
			self._jsondata = json.load(urllib2.urlopen(self.getJsonBingWallpaperUrl()))
			assert "images" in self._jsondata, 'script seems outdated'
		return self._jsondata

	def getJsonBingWallpaperUrl(self):
		return _BASE_JSON_BING_WALLPAPER_URL.format(self._id, self._lang)

	def download(self):
		imagejson = self.jsondata['images'][0]
		url = 'http://www.bing.com/{}_{}.jpg'.format(imagejson['urlbase'], get_formated_screen_size())
		path = "{}.jpg".format(imagejson["fullstartdate"])

		if not os.path.isdir(BASE_PATH):
			os.mkdir(BASE_PATH)

		path = os.path.join(BASE_PATH, path)

		urllib.urlretrieve(url, path)  # download
		return path


def main():
	dl = BingWallpaper()
	path = dl.download()
	set_background_wallpaper(path)

if __name__ == '__main__':
	main()
