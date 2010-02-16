#!/usr/bin/env python
# coding=UTF-8

import cgi
import os
import sys
import time

import CaptchasDotNet

def sign_pseudonym(pseudonym):
    ''' Takes a pseudonym and signs it using some GPG and timestamp magic '''
    pseudonym += str(time.time()).strip()
    return pseudonym

def create_pseudonym():
    ''' For now just returns a random string. '''
    process = os.popen("makepasswd")
    return process.read().strip()

def create_captcha():
    ''' Returns the HTML for a captcha '''
    captchas = CaptchasDotNet.CaptchasDotNet (
                                client   = 'demo', 
                                secret   = 'secret'
                                )    
    captcha = '''
    <form method="get" action="pm.cgi">
    <table>
      <tr>
        <td>
          <input type="hidden" name="random" value="%s" />
        </td>
      </tr>
      <tr>
        <td>
          The CAPTCHA password:
        </td>
        <td>
          <input name="password" size="16" />
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td>
           %s <br>
           <a href="%s">Phonetic spelling (mp3)</a>
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td>
          <input type="submit" value="Submit" />
        </td>
      </tr>
    </table> ''' % (captchas.random (), captchas.image (), captchas.audio_url ())

    return captcha

def validate_captcha():
    captchas = CaptchasDotNet.CaptchasDotNet (
                                client   = 'demo',
                                secret   = 'secret'
                                )

    # Read the form values and keep empty fields.
    form = cgi.FieldStorage(keep_blank_values = True)
    try:
        # message = form['message'].value
        password = form['password'].value
        random_string = form['random'].value
    except KeyError:
        # Return an error message, when reading the form values fails.
        #return 'Invalid arguments.'
        return False

    # Check the random string to be valid and return an error message
    # otherwise.
    if not captchas.validate (random_string):
        #return ('Every CAPTCHA can only be used once. The current '
        #        + 'CAPTCHA has already been used. Try again.')
        return False

    # Check, that the right CAPTCHA password has been entered and
    # return an error message otherwise.
    if not captchas.verify (password):
        #return ('You entered the wrong password. '
        #        + 'Please use back button and try again.')
        return False

    # Return a success message.
    #return ('Your message was verified to be entered by a human '
    #        + 'and is "%s"' % message)
    return True


def index():
    """ Return the user interface for the pseudonym manager in HTML """
    # Display error messages in browser for easy debugging
    sys.stderr = sys.stdout

    pmi = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN\" 
    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">
    <html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">
    <head><meta http-equiv="Content-type" content="text/html;charset=UTF-8" /> 
    <title>Pseudonym Manager</title></head><body><h4>Pseudonym Manager</h4>
    '''
    
    captcha = create_captcha()
    if validate_captcha():
        pmi += "<h1>Your pseudonym is " + sign_pseudonym(create_pseudonym()) + "</h1>"
    else:
        pmi += captcha
        pmi += "<br/>Captcha validation failed or form was blank. Try again."


    pmi += '</body></html>'
    
    return pmi

print "Content-type: text/html\n\n";
print index()

