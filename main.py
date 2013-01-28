import mechanize
import memcache
import settings
import RoyalMail
from BeautifulSoup import BeautifulSoup
from datetime import date
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

def get_data(data):
	if data != mc.get(settings.name):
		mc.set(settings.name, data)
		body = 'Info:\n\n'
		for i in data:
			body += i + '\n'
		body += '\nThanks!\nMechenz'
		RoyalMail.sendMail([settings.to], 'Mechenz | ' + str(date.today()) + ' | ' + settings.name, body)
	
def main():
	browser = mechanize.Browser()
	browser.addheaders = [('User-agent', settings.fake_user_agent), ('Referer', settings.fake_referer)]
	browser.set_handle_robots(False)
	browser.open(settings.site)
	browser.select_form(nr=0)
	for i,v in (settings.form).iteritems():
		browser.form[i] = v
	req = browser.submit()
	response = browser.open(settings.form_url)
	html = response.read()
	soup = BeautifulSoup(html)
	data = []
	for i in soup.findAll('div', {'class': 'action'}):
		names = i.findAll('span')
		try:
			data.append(names[0].text)
		except IndexError:
			pass
	get_data(data)

if __name__ == '__main__':
	main()