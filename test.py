import smtplib
carriers = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
}

def send(message, number, carrier):
	to_number = f'{number}{carriers[carrier]}'
	auth = ('thelockerioapp@gmail.com', 'TheLocker789')
	
	server = smtplib.SMTP( "smtp.gmail.com", 587 )
	server.starttls()
	server.login(auth[0], auth[1])
	
	server.sendmail( auth[0], to_number, message)
	print("Sent")

for i in range(5):
	send("Hello", "7038321922", "tmobile")
	send("Hello", "7033388179", "att")
