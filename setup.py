from distutils.core import setup
import py2app

NAME = 'Gwitter'
SCRIPT = 'gwitter.py'
VERSION = '0.1'
ID = 'gwitter'

plist = dict(
     CFBundleName                = NAME,
     CFBundleShortVersionString  = ' '.join([NAME, VERSION]),
     CFBundleGetInfoString       = NAME,
     CFBundleExecutable          = NAME,
     CFBundleIdentifier          = 'com.example.albertb.%s' % ID,
     LSUIElement                 = '1'
)

app_data = dict(script=SCRIPT, plist=plist)

setup(
   app = [app_data],
)
