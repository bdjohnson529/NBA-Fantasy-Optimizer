from bs4 import BeautifulSoup, Comment
from urllib2 import urlopen
import ssl


def soupify(url):
	#open
	ctx = verify_false()
	# soupify
	html = urlopen(url, context=ctx).read()
	soup = BeautifulSoup(html, "lxml")
	return soup

def verify_false():
	#verify set to false (not secure but doesn't really matter for this)
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	return ctx