#!/usr/bin/python
#
# Author: Runa Sandvik, <runa.sandvik@gmail.com>
#
# See LICENSE for licensing information.
#
# The function verify_captcha is from http://captchas.net/sample/python.
# The sample implementation on that page is freeware.
#
# This script will verify the string entered by the user. If the correct
# string has been entered, a file with a random string will be written,
# signed with GPG and printed to the user.
#

# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement

# Start with importing the necessary modules
import CaptchasDotNet
import cgi
import GnuPGInterface
import random

# Define GnuPGInterface
gnupg = GnuPGInterface.GnuPG()

### Start config ###

# Tell gnupg where to find the GPG keyring. That is, the .gnupg
# directory. Do not add the trailing slash.
gnupg.options.homedir = ""

# The secret passphrase of the GPG key
passphrase = ""

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

# If the string entered by the user was correct, create a random string,
# write it to a file, sign the file with GPG and return the output.
def create_and_sign():
    """Create a random string, write it to a file, sign with GPG and
    return the output"""
    # Where to find the passphrase to use when signing the file
    gnupg.passphrase = passphrase

    # Create the random string. The string will consist of small
    # letters, big letters and digits.
    letters = "abcdefghijklmnopqrstuvwxyz"
    letters += letters.upper () + "0123456789"

    # 40 random possible characters are appended.
    randstr = "Random string: "
    for i in range(40):
        randstr += random.choice(letters)

    # Write the random string to a file so that it can be signed with
    # GPG later. The file, with a random name, will be written to /tmp.
    # Define randstr_file as global because verify_captcha() needs it.
    global randstr_file
    randstr_file ="/tmp/"
    for i in range(10):
        randstr_file += random.choice(letters)

    # Write random string to file
    with open(randstr_file, 'w') as write_randstr:
        write_randstr.write(randstr)

    # Open the file to read the contents
    sign_file = open(randstr_file, 'r')

    # Sign the file
    clearsign = gnupg.run(['--no-tty'], ['--clearsign'],
            create_fhs=['stdout'], attach_fhs={'stdin': sign_file})

    # Read the output, i.e. the signature, so that it can be stored
    # later.
    signature = clearsign.handles['stdout'].read()

    # Write the output to the original file.
    with open(randstr_file, 'w') as write_signature:
        write_signature.write(signature)

# Validate and verify the input from the user
def verify_captcha ():
    """Validate and verify user input"""
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
        create_and_sign()

        # Read the contents of the signed file and return it to the
	    # user.
        with open(randstr_file, 'r') as read_randstr:
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
''' % verify_captcha ()
