#!/usr/bin/python
#
# Author:  Runa A. Sandvik, <runa.sandvik@gmail.com>
#
# See LICENSE for licensing information.
#
# This script will ask the user for the contents of file.asc,
# then try to verify the signature using GPG.

# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement

# Import the necessary modules
import GnuPGInterface
import random

# Define GnuPGInterface
gnupg = GnuPGInterface.GnuPG()

### Start config ###

# Tell gnupg where to find the GPG keyring. That is, the .gnupg
# directory. Do not add the trailing slash.
gnupg.options.homedir = ""

# The ID of the key that was used to sign the user input.
keyid = ""

### End config ###

def verify():
    """Verify signature of user input using GPG"""
    # Read signature from user input
    user_input = []
    entry = raw_input("Enter signature, 'done' on its own line when you are finished: \n")
    while entry != "done":
        user_input.append(entry)
        entry = raw_input("")
    user_input = '\n'.join(user_input)

    # Write user input to a random file in /tmp, so that the signature
    # can be verified later on. Use small letters, big letters and
    # digits for the filename.
    letters = "abcdefghijklmnopqrstuvwxyz"
    letters += letters.upper () + "0123456789"

    # Actually write user input to file
    input_file = "/tmp/"
    for i in range(10):
        input_file += random.choice(letters)
    with open(input_file, 'w') as write_input:
        write_input.write(user_input)

    # Open the file to read the contents
    verify = open(input_file, 'r')

    # Verify the signature
    clearsign = gnupg.run(['--no-tty'], ['--decrypt'],
    create_fhs=['stdout','stderr'], attach_fhs={'stdin': verify})

    # Read the output from gnupg, and split it into an array so that it
    # can be evaluated.
    signature = clearsign.handles['stderr'].read()
    s = signature.split()

    # The signature can not be checked if the public key is not found
    if "public key not found" in signature:
        print "It seems like the key has not been imported"

    # Check if the signature is valid. Do not accept a bad signature.
    if "BAD" in signature:
        print "Sorry, this signature is not valid"

    # Accept a good signature if it is signed by the right key ID. If it
    # is a good signature, and the right key ID have been used, check
    # when the signature was made.
    if "Good" in signature and keyid in s[14]:
            print "Good signature made", s[4], s[5], s[6], s[7], s[8], s[9]

# Main function
if __name__ == "__main__":
    verify()
