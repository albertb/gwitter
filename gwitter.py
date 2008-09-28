#!/usr/bin/env python
#
# Copyright 2008 Albert Bachand.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A simple app that checks Twitter for new tweets, and sends them to Growl."""

__author__ = '"Albert Bachand" <albertb@gmail.com>'
__version__ = '0.1'

import Growl
import time
import re
import subprocess
import twitter
import urllib

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

class Gwitter(NSObject):
  
  def initWithArgs_(self, username, password, interval=300):
    """ObjC-style constructor for Gwitter.
    
    Args:
      username: str. Twitter username.
      password: str. Twitter password.
      interval: int. How often to check for new tweets, in seconds.
    Returns:
      self.
    """
    self.init()
    self.__growl = Growl.GrowlNotifier('Gwitter', ['Tweet'])
    self.__twitter = twitter.Api(username=username, password=password)
    self.__interval = interval
    self.__since = None
    self.__icons = {}
    return self
  
  def applicationDidFinishLaunching_(self, notification):
    """Called by Cocoa when the app is done loading."""
    self.__bar = NSStatusBar.systemStatusBar()
    self.__item = self.__bar.statusItemWithLength_(NSVariableStatusItemLength)
    self.__item.setToolTip_('Gwitter')
    self.__item.setAction_('terminate:')
    self.__item.setTitle_('G') # TODO: Icon instead
    self.__timer = (NSTimer.alloc().
        initWithFireDate_interval_target_selector_userInfo_repeats_(
            NSDate.date(), self.__interval, self, 'update:', None, True))
    NSRunLoop.currentRunLoop().addTimer_forMode_(self.__timer,
                                                 NSDefaultRunLoopMode)
    self.__timer.fire()
  
  def update_(self, notification):
    """Called by the Cocoa timer, at regular intervals."""
    self.__GrowlNewTweets()
      
  def __GrowlNewTweets(self):
    """Checks twitter for new tweets, and sends them to Growl."""
    tweets = self.__twitter.GetFriendsTimeline(since=self.__since)
    self.__since = time.asctime(time.gmtime())
    for tweet in tweets:
      self.__growl.notify('Tweet',
                          '%s says:' % tweet.user.name,
                          tweet.text,
                          self.__GetProfileIcon(tweet.user))
  
  def __GetProfileIcon(self, user):
    """Gets the profile icon for a user.
    
    Args:
      user: obj. The Twitter.User object for which to return the profile icon.
    Returns:
      The profile icon, wrapped in a Growl.Image.
    """
    if not self.__icons.has_key(user.name):
      try :
        image = urllib.urlopen(user.profile_image_url).read()
      except:
        image = ''
      self.__icons[user.name] = Growl.Image.imageWithData(image)
    return self.__icons.get(user.name)
  
def FindInternetPassword(server):
  """Finds the internet username/password for the specified server.
  TODO(albertb): Replace this by calls to the Keychain API.
  
  Args:
    server: str. The server to get the username/password for.
  Returns:
    A tuple of the form (username, password).
  """
  p = subprocess.Popen(['/usr/bin/security',
                        'find-internet-password', '-gs', server],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  for line in p.stdout:
    m = re.match('\s+"acct"<blob>="([^"]+)"', line)
    if not m is None:
      username = m.group(1)
      break
  for line in p.stderr:
    m = re.match('password: "([^"]+)"', line)
    if not m is None:
      password = m.group(1)
      break
  return (username, password)

if __name__ == '__main__':
  credentials = FindInternetPassword('twitter.com')
  app = NSApplication.sharedApplication()
  delegate = Gwitter.alloc().initWithArgs_(credentials[0], credentials[1], 300)
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()