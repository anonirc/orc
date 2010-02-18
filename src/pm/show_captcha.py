#!/usr/bin/python
#
# The majority of the code in this file is from
# http://captchas.net/sample/python/. However, the rest is written by
# Runa Sandvik, <runa.sandvik@gmail.com>
#

# This script will simply show the user the captcha
# Start with importing the necessary modules
import CaptchasDotNet

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

# Print fancy html page
print 'Content-Type: text/html'
print
print '''
<html>
  <head><title>ORC: Request for pseudonym</title></head>
  <p>We would like to verify that you are in fact human</p>
  <form method="get" action="verify_captcha.cgi">
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
    </table>
  </form>
</html>
''' % (captchas.random (), captchas.image (), captchas.audio_url ())
