# **************************************************************************
# *                                                                        *
# *     MicroPython high-level 'hid' module                                *
# *                                                                        *
# **************************************************************************
# *                                                                        *
# *     This is the high level handler for HID over USB. This module uses  *
# *     the lower level "_hid" module to deliver its functionality.        *
# *                                                                        *
# **************************************************************************

PRODUCT = "High-Level HID Interface"
PACKAGE = "hid"
PROGRAM = "hid.py"
VERSION = "0.02"
CHANGES = "0000"
TOUCHED = "0000-00-00 00:00:00"
LICENSE = "MIT Licensed"
DETAILS = "https://opensource.org/licenses/MIT"

# .------------------------------------------------------------------------.
# |    MIT Licence                                                         |
# `------------------------------------------------------------------------'

# Copyright 2021, "Hippy"

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

try    : import _hid
except : _hid = None

import time

DEBUG = False or (_hid == None)

MOD_NONE   = 0x00
MOD_LCTRL  = 0x01
MOD_LSHIFT = 0x02
MOD_LALT   = 0x04
MOD_LMETA  = 0x08
MOD_RCTRL  = 0x10
MOD_RSHIFT = 0x20
MOD_RALT   = 0x40
MOD_RMETA  = 0x80

keyCodes = [0] * 256
keyNames = {}
modNames = {}

modifier = MOD_NONE
sendTime = -1

# .-----------------------------------------------------------------------.
# |     Define the keycodes to be sent per ASCII character                |
# `-----------------------------------------------------------------------'

def SetKeyCode(adr, s, mod=0, sub=0):
  if s.find("..") == 1:
    for n in range(ord(s[0]), ord(s[-1])+1):
      SetKeyCode(adr, chr(n), mod, sub)
      adr = adr + 1
  else:
    for c in s:
      keyCodes[ord(c) - sub] = (mod << 8) | adr
      adr = adr + 1

def SetKeyCodes():
  SetKeyCode(0x04, "a..z")
  SetKeyCode(0x04, "A..Z", MOD_LSHIFT)
  SetKeyCode(0x04, "A..Z", MOD_LCTRL, ord("A") - 1)
  SetKeyCode(0x1E, '!"£$%^&*()', MOD_LSHIFT)
  SetKeyCode(0x1E, "1234567890")
  SetKeyCode(0x28, "\n")
  SetKeyCode(0x2C, " ")
  SetKeyCode(0x2D, "_+{}" + "|"  + "~:@¬<>?", MOD_LSHIFT)
  SetKeyCode(0x2D, "-=[]" + "\\" + "#;'`,./")
  SetKeyCode(0x29, chr(0x1B)           ) # Ctrl-[ ESC
  SetKeyCode(0x31, chr(0x1C), MOD_LCTRL) # Ctrl-\ FS
  SetKeyCode(0x30, chr(0x1D), MOD_LCTRL) # Ctrl-] GS
  SetKeyCode(0x23, chr(0x1E), MOD_LCTRL) # Ctrl-^ RS
  SetKeyCode(0x2D, chr(0x1F), MOD_LCTRL) # Ctrl-_ US
  SetKeyCode(0x34, chr(0x00), MOD_LCTRL) # Ctrl-@ NUL

# .-----------------------------------------------------------------------.
# |     Define the names of non-ASCII keys                                |
# `-----------------------------------------------------------------------'

def SetKeyName(adr, nam, mod=0):
  keyNames[nam] = (mod << 8) + adr

def SetKeyNames():
  SetKeyName(0x02, "POST-FAIL")
  SetKeyName(0x03, "ERROR")
  SetKeyName(0x28, "ENTER")
  SetKeyName(0x28, "RETURN")
  SetKeyName(0x29, "ESC")
  SetKeyName(0x29, "ESCAPE")
  SetKeyName(0x2A, "BS")
  SetKeyName(0x2A, "BACK-SPACE")
  SetKeyName(0x2B, "TAB")
  SetKeyName(0x2B, "UN-TAB", MOD_LSHIFT)
  SetKeyName(0x2C, "SPACE")
  SetKeyName(0x39, "CAPS-LOCK")
  for n in range(12): # Function keys F1 to F12
    SetKeyName(0x3A + n, "F" + str(n + 1))
  SetKeyName(0x46, "PRTSC", MOD_LSHIFT)
  SetKeyName(0x46, "SYSRQ")
  SetKeyName(0x47, "SCROLL-LOCK")
  SetKeyName(0x48, "PAUSE", MOD_LSHIFT)
  SetKeyName(0x48, "BREAK")
  SetKeyName(0x49, "INSERT")
  SetKeyName(0x4A, "HOME")
  SetKeyName(0x4B, "PGUP")
  SetKeyName(0x4B, "PAGE-UP")
  SetKeyName(0x4C, "DEL")
  SetKeyName(0x4C, "DELETE")
  SetKeyName(0x4D, "END")
  SetKeyName(0x4E, "PGDN")
  SetKeyName(0x4E, "PAGE-DOWN")
  SetKeyName(0x4F, "RIGHT")
  SetKeyName(0x50, "LEFT")
  SetKeyName(0x51, "DOWN")
  SetKeyName(0x52, "UP")
  SetKeyName(0x53, "NUM-LOCK")
  for n in range(12): # Function keys F13 to F24
    SetKeyName(0x68 + n, "F" + str(13 + n))

# .-----------------------------------------------------------------------.
# |     Define the named modifiers which can be used                      |
# `-----------------------------------------------------------------------'

def SetModNames():
  modNames[ "NORMAL"         ] = MOD_NONE
  modNames[ "CTRL"           ] =                         MOD_LCTRL          
  modNames[ "CTRL-SHIFT"     ] =            MOD_LSHIFT + MOD_LCTRL  
  modNames[ "CTRL-SHIFT-ALT" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL     
  modNames[ "CTRL-ALT"       ] = MOD_LALT              + MOD_LCTRL                
  modNames[ "CTRL-ALT-SHIFT" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL     
  modNames[ "SHIFT"          ] =            MOD_LSHIFT            
  modNames[ "SHIFT-CTRL"     ] =            MOD_LSHIFT + MOD_LCTRL  
  modNames[ "SHIFT-CTRL-ALT" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL     
  modNames[ "SHIFT-ALT"      ] = MOD_LALT + MOD_LSHIFT                       
  modNames[ "SHIFT-ALT-CTRL" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL     
  modNames[ "ALT"            ] = MOD_LALT                                    
  modNames[ "ALT-SHIFT"      ] = MOD_LALT + MOD_LSHIFT                        
  modNames[ "ALT-SHIFT-CTRL" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL     
  modNames[ "ALT-CTRL"       ] = MOD_LALT              + MOD_LCTRL                
  modNames[ "ALT-CTRL-SHIFT" ] = MOD_LALT + MOD_LSHIFT + MOD_LCTRL

# .-----------------------------------------------------------------------.
# |     Send a single key press                                           |
# `-----------------------------------------------------------------------'

def SendKey(k):
  global sendTime
  if DEBUG:
    s = "Unknown"
    for this in modNames:
      if (modifier | (k >> 8)) == modNames[this]:
        s = this
        break
    print("SendKey {} {} {}".format(Hex(modifier | (k >> 8), 2), s, Hex(k & 0xFF, 2)))
  elif k != 0:
    if sendTime >= 0:
      while time.ticks_diff(time.ticks_ms(), sendTime) < 20:
        time.sleep_ms(1)
    _hid.keypress(modifier | (k >> 8), k & 0xFF)
    time.sleep_ms(20)
    _hid.keypress(0, 0)
    sendTime = time.ticks_ms()

# .-----------------------------------------------------------------------.
# |     Send the key representing a single ASCII character                |
# `-----------------------------------------------------------------------'

def SendChar(c):
  SendKey(keyCodes[ord(c) & 0xFF])

# .-----------------------------------------------------------------------.
# |     Handle a single word sent                                         |
# `-----------------------------------------------------------------------'

def SendWord(s):
  global modifier
  if isinstance(s, int):
    s = str(s)
  else:
    u = s.upper()
    if u in modNames:
      if DEBUG:
        print("[1] {} is in modNames ({}) - Add modifier".format(u, modNames[u]))
      modifier = modifier | modNames[u]
      return
    if u in keyNames:
      if DEBUG:
        print("[2] {} is in keynames ({}) - send as key".format(u, keyNames[u]))
      SendKey(keyNames[u])
      return
    n = u.rfind("-")
    if n > 0:
      mod, key = u[:n], u[n+1:]
      if DEBUG:
        print("[3] {} might be split '{}' + '{}'".format(u, mod, key))
      if mod in modNames:
        if DEBUG:
          print("[4] {} is in modNames ({})".format(mod, modNames[mod]))
        if key in keyNames:
          if DEBUG:
            print("[5] {} is in keyNames ({}) - Send as named key".format(key, keyNames[key]))
          SendKey(keyNames[key] | (modNames[mod] << 8))
          return
        modifier = modNames[mod]
        s = s[n+1:]
      if DEBUG:
        print("[6] This is modifier {} ({}) plus non-key '{}'".format(mod, modNames[mod], s))
      if len(s) == 1 and s != s.lower():
        if mod in["CTRL", "ALT", "CTRL-ALT", "ALT-CTRL"]:
          # We want to convert 'CTRL-A' etc to actually be 'CTRL-a' so we don't
          # get a SHIFT with it. If one wants a 'CTRL-SHIFT' then specify that
          # rather than just 'CTRL'.
          if DEBUG:
            print("[7] Changing '{}-{}' to '{}-{}'".format(mod, s, mod, s.lower()))
          s = s.lower()
  if DEBUG:
    print("[8] Send individual characters '{}'".format(s))
  for c in s:
    SendChar(c)
  modifier = MOD_NONE

# .-----------------------------------------------------------------------.
# |     Send a sequence of words                                          |
# `-----------------------------------------------------------------------'

def Send(arg, *args):
  global modifier; modifier = MOD_NONE
  SendWord(arg)
  for arg in args:
    SendWord(arg)

# .-----------------------------------------------------------------------.
# |     Initialise the keyboard lookup tables                             |
# `-----------------------------------------------------------------------'

SetKeyCodes()
SetKeyNames()
SetModNames()

# .-----------------------------------------------------------------------.
# |     Mouse handler                                                     |
# `-----------------------------------------------------------------------'

def Move(up=0, down=0, left=0, right=0):
  def Limit(max, n):
    if n < -max : return -max
    if n >  max : return  max
    return n
  up    = Limit(127, up - down)
  right = Limit(127, right - left)
  _hid.move(up, right)
  
# .-----------------------------------------------------------------------.
# |     If running this code we either want to see the results on a Pi or |
# |     PC or we want to test it out on a Pico                            |
# `-----------------------------------------------------------------------'

if __name__ == "__main__":
  if DEBUG:
    def Hex(n, w):
      s = hex(n)[2:].upper()
      if len(s) < w:
        s = ("0" * (w-len(s))) + s
      return s
    def Test(*args):
      print("")
      print(", ".join(args))
      Send(*args)
    for n in range(len(keyCodes)):
      if   n < 0x20 : desc = "\t" + "Ctrl-" + chr(n + ord("A") - 1)
      elif n < 0x7F : desc = "\t" + chr(n)
      else          : desc = ""
      print("keyCodes[{}] = {}{}".format(Hex(n,2), Hex(keyCodes[n],2), desc))
    print("")
    for this in keyNames:
      print("keyNames['{}'] = {}".format(this, Hex(keyNames[this],2)))
    print("")
    for this in modNames:
      print("modNames['{}'] = {}".format(this, Hex(modNames[this],2)))
    Test("a")
    Test("A")
    Test("SHIFT-a")
    Test("CTRL-a")
    Test("ALT-a")
    Test("SHIFT-A")
    Test("CTRL-A")
    Test("ALT-A")
    Test("HOME")
    Test("SHIFT-HOME")
    Test("CTRL-HOME")
    Test("ALT-HOME")
    Test("SHIFT", "CTRL", "ALT-HOME")
    Test("abc", "CTRL", "abc", "abc")
    Test("abc", "CTRL", "ALT", "abc", "abc")
    Test("abc", "CTRL-ALT", "abc", "abc")
    Test("abc", "CTRL-c", "CTRL-C", "abc\n")
  else:
    time.sleep(5)
    while True:
      time.sleep(5)
      if True:
        Send("# Hello", "CTRL-C")
        Send("# Hello World!\n")
      if True:
        time.sleep(2)
        Move(up=200)
        time.sleep(2)
        Move(right=200)
        time.sleep(2)
        Move(down=200)
        time.sleep(2)
        Move(left=200)
        time.sleep(2)
