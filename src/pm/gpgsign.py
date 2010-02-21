#!/usr/bin/python
#
# Author: Runa Sandvik, <runa.sandvik@gmail.com>
#
# See LICENSE for licensing information.
#
# This script will create a file with a random string, sign the file
# with 'gpg --clearsign' and then save the output in the original file.
#

# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement

# Import the rest of the necessary modules
import GnuPGInterface
import random

# Define GnuPGInterface
gnupg = GnuPGInterface.GnuPG()

### Start config ###

# Tell gnupg where to find the GPG keyring. That is, the .gnupg
# directory. Do not add the trailing slash.
gnupg.options.homedir = ""

# The secret passphrase of the GPG key.
passphrase = ""

### End config ###

# Where to find the passphrase to use when signing the file.
gnupg.passphrase = passphrase

# Create the random string. The string will consist of small letters,
# big letters and digits.
letters = "abcdefghijklmnopqrstuvwxyz"
letters += letters.upper () + "0123456789"

# The random starts out empty, then 40 random possible characters are
# appended.
randstr = "Random string: "
for i in range(40):
	randstr += random.choice(letters)

# Write the random string to a file so that it can be signed with GPG
# later. The file, with a random name, will be written to /tmp.
randstr_file ="/tmp/"
for i in range(10):
	randstr_file += random.choice(letters)

# Write random string to file
with open(randstr_file, 'w') as write_randstr:
    write_randstr.write(randstr)

# Open the file to read the contents
sign_file = open(randstr_file, 'r')

# Sign the file
clearsign = gnupg.run(['--no-tty'], ['--clearsign'], create_fhs=['stdout'],
		attach_fhs={'stdin': sign_file})

# Read the output, i.e. the signature, so that it can be stored later.
signature = clearsign.handles['stdout'].read()

# Write the output to the original file.
with open(randstr_file, 'w') as write_signature:
    write_signature.write(signature)
