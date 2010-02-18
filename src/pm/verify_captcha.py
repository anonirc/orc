#!/usr/bin/python
#
# The majority of the code in this file is from http://captchas.net/sample/python.
# However, the rest is written by Runa Sandvik, <runa.sandvik@gmail.com>
#

# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement

# This script will verify the string entered by the user
# Start with importing the necessary modules
import CaptchasDotNet
import cgi
import gpgsign
import subprocess

### Start config ###

# Set the path to gpgsign.py
gpgsign_path = ""

# Construct the captchas object. Replace the required parameteres 'demo'
# and 'secret' with the values you receive upon registration at
# http://captchas.net
captchas = CaptchasDotNet.CaptchasDotNet (
		client = 'demo',
		secret = 'secret'
#		alphabet = 'abcdefghkmnopqrstuvwxyz'
#		letters = 6,
#		width = 240,
#		height = 80
		)

### End config ###

# Validate and verify the input from the user
def get_body ():

    # Read the form values and keep empty fields.
    form = cgi.FieldStorage(keep_blank_values = True)
    try:
        password = form['password'].value
        random_string = form['random'].value
    except KeyError:
    	# Return an error message, when reading the form values fails.
        return 'Invalid arguments.'

    # Check the random string to be valid and return an error message
    # otherwise.
    if not captchas.validate (random_string):
        return ('Every CAPTCHA can only be used once. The current '
                + 'CAPTCHA has already been used. Try again.')

    # Check, that the right CAPTCHA password has been entered and
    # return an error message otherwise.
    if not captchas.verify (password):
        return ('You entered the wrong password. '
                + 'Please use back button and try again.')

    # If the right CAPTCHA has been entered, run gpgsign.py to generate
    # a random string and sign it with GPG.
    if captchas.verify(password):
	    cmd = ['python', gpgsign_path]
	    subprocess.Popen(cmd)

	    # Read the contents of the signed file and return it to the
	    # user.
	    with open(gpgsign.randstr_file, 'r') as read_randstr:
		    return read_randstr.read()

# Print a fancy html page
print 'Content-Type: text/html'
print
print '''
<html>
  <head>
	<title>ORC: Request for pseudonym</title>
  </head>
    <pre>%s</pre>
</html>
''' % get_body ()
