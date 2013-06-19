# https://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
# http://forum.codecall.net/topic/59608-developing-a-basic-irc-bot-with-python/
# http://docs.python.org/2/library/ssl.html
# http://docs.python.org/2/library/hashlib.html
# https://www.hackthissite.org/articles/read/1050
# http://stackoverflow.com/questions/4719438/editing-specific-line-in-text-file-in-python

'''
@author: b0nk
@version: 1.1
'''

# Import the necessary libraries.
import socket
import ssl
import hashlib
import time
import random
import string

# Other imports
# Imports for last.fm methods
# https://code.google.com/p/pylast/
import pylast

# Imports for google search
#import urllib
#import json

# Imports for feeds
# Twitter
import twitter

# Some basic variables used to configure the bot

server = "boxxybabee.catiechat.net" # EU server
#server = "anewhopeee.catiechat.net" # US server
port = 6667 # default port
ssl_port = 6697 # ssl port
chans = ["#test", "#music", "#boxxy", "#IdleRPG"] #default channels
botnick = "testbot" # bot nick
botuser = "I"
bothost = "m.botxxy.you.see"
botserver = "testserver"
botname = "testname"
botpassword = "bawksy"
quitmsg = "Exited_normally!"

# Global vars

nicks = []

authDB = []
authUsrs = []
ignUsrs = []
greets = []
parts = []
eightball = []
quotes = []
lfmUsers = []

taggers = []
tagged = ''
prevTagged = ''
isTagOn = False
lastCommand = ''
tmpstr = ''
rosestr = "3---<-<-{4@"
boobsstr = "(.Y.)"
prompt = ">> "

# Last.fm vars

lfm_logo = "0,5last.fm "
cmp_bars = ["[4====            ]",
            "[4====7====        ]",
            "[4====7====8====    ]",
            "[4====7====8====9====]",
            "[                ]"]
lastfm = None

# Google vars

g_logo = "12G4o8o12g9l4e "
g_baseURL = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="

# Twitter vars
t_logo = "0,10twitter "
t_api = None

#============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============

def ping(reply): # This is our first function! It will respond to server Pings.
  ircsock.send("PONG :" + reply + '\n') # In some IRCds it is mandatory to reply to PING the same message we recieve
  #print prompt + "PONG :" + reply

def sendChanMsg(chan, msg): # This sends a message to the channel 'chan'
  ircsock.send("PRIVMSG " + chan + " :" + msg + '\n')
  
def sendNickMsg(nick, msg): # This sends a notice to the nickname 'nick'
  ircsock.send("NOTICE " + nick + " :" + msg + '\n')
  
def getNick(msg): # Returns the nickname of whoever requested a command from a RAW irc privmsg. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split('!')[0].replace(':','')

def getUser(msg): # Returns the user and host of whoever requested a command from a RAW irc privmsg. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[0].translate(None, ':')

def getChannel(msg): # Returns the channel from whereever a command was requested from a RAW irc PRIVMSG. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[-1].split(' :')[0]

def joinChan(chan): # This function is used to join channels.
  ircsock.send("JOIN " + chan + '\n')

def joinChans(chans): # This is used to join all the channels in the array 'chans'
  for i in chans:
    ircsock.send("JOIN " + i + '\n')

def hello(msg): # This function responds to a user that inputs "Hello testbot"
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    print prompt + nick + " said hi in " + chan
    sendChanMsg(chan, "Hello " + nick + "! Type !help for more information.")
  
def identify():
  ircsock.send("NICK " + botnick + '\n') # Here we actually assign the nick to the bot
  time.sleep(3)
  ircsock.send("NICKSERV IDENTIFY " + botpassword + '\n') # Identifies the bot's nickname with nickserv
  print prompt + "Bot identified"

#========================END OF BASIC FUNCTIONS=====================

#========================INITIALIZATIONS============================

def idleRPG():
  ircsock.send("PRIVMSG IdleBot :LOGIN derpbot 123456\n")
  print prompt + "Logged in to IdleRPG"

# Authorized

def loadAuth():
  global authDB
  authDB = [line.strip() for line in open('auth.txt', 'r')]
  print prompt + "Auth -> LOADED"

# Ignores
  
def loadIgn():
  global ignUsrs
  ignUsrs = [line.strip() for line in open('ign.txt', 'r')]
  print prompt + "Ign -> " + ignUsrs.__str__()
  
# Greets

def loadGreets():
  global greets
  greets = [line.strip() for line in open('greet.txt', 'r')]
  print prompt + "Greets -> LOADED"
  
# Parts
  
def loadParts():
  global parts
  parts = [line.strip() for line in open('part.txt', 'r')]
  print prompt + "Parts -> LOADED"
  
# 8ball

def load8ball():
  global eightball
  eightball = [line.strip() for line in open('8ball.txt', 'r')]
  print prompt + "8ball -> LOADED"
  
# Quotes

def loadQuotes():
  global quotes
  quotes = [line.strip() for line in open('quotes.txt', 'r')]
  print prompt + "Quotes -> LOADED"
  
# Last.fm Users

def loadLfmUsers():
  global lfmUsers
  lfmUsers = [line.strip() for line in open('lfmusers.txt', 'r')]
  print prompt + "LfmUsers -> LOADED"
  
def loadLfm():
  lines = [line.strip() for line in open('lfm.txt', 'r')]
  API_KEY = filter(lambda x: x in string.printable, lines[0])
  API_SEC = lines[1]
  global lastfm
  lastfm = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SEC, username = '', password_hash = '')
  print prompt + "last.fm interface -> LOADED"
  
def loadTwitter():
  lines = [line.strip() for line in open('twitter.txt', 'r')]
  CON_KEY = filter(lambda x: x in string.printable, lines[0])
  CON_SEC = lines[1]
  ACC_TOK = lines[2]
  ACC_SEC = lines[3]
  global t_api
  t_api = twitter.Api(consumer_key = CON_KEY, consumer_secret = CON_SEC, access_token_key = ACC_TOK, access_token_secret = ACC_SEC)
  print prompt + "twitter API -> LOADED"

#========================END OF INITIALIZATIONS=====================

          #AUTHENTICATION

def authCmd(msg): # Authenticates a nick with the bot
  nick = getNick(msg)
  if nick not in ignUsrs:
    global authDB, authUsrs
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      for i, content in enumerate(authDB):
        if nick + "|!|" in content:
          authDB[i] = None
          authDB.remove(None)
          authUsrs.remove(nick)
          print prompt + authDB.__str__()
          with open("auth.txt", 'w') as f:
            for i in authDB:
              f.write('%s\n' % i)
              f.closed
              
          sendChanMsg(chan, "Password deleted you dumbass!!!")
          sendNickMsg(nick, "Request a new password.")
    else:
      # ":b0nk!LoC@fake.dimension PRIVMSG :!pass password"
      password = msg.split("!pass")[1].lstrip(' ') # RAW password
      if not password:
        sendNickMsg(nick, "Bad arguments. Usage: !pass <password>")
      else:
        password = hashlib.sha256(password).hexdigest() # A HEX representation of the SHA-256 encrypted password
        print prompt + "ENC: " + password
        
        for i, content in enumerate(authDB):
          if nick + "|!|" + password in content:
            authUsrs.append(nick)
            print prompt + nick + " is authorized.\n" + prompt + authUsrs.__str__()
            sendNickMsg(nick, "Password correct.")
            return None

        print prompt + nick + " mistyped the password"
        sendNickMsg(nick, "Password incorrect!")

          #INVITE

def inviteCmd(msg): # Parses the message to extract NICK and CHANNEL
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :!invite "
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !invite outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!invite")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to invite
        sendChanMsg(chan, "Bad arguments. Usage: !invite <nick>")
      else: # Success
        print prompt + "Inviting " + target + " to channel " + chan
        sendChanMsg(chan, "Inviting " + target + " here...")
        invite(target,chan)
  
def invite(nick,chan): # Invites given nickname to present channel
  ircsock.send("INVITE " + nick + ' ' + chan + '\n')

          #VOICE

def voiceCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !voice outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!voice")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to voice
        sendChanMsg(chan, "Bad arguments. Usage: !voice <nick>")
      else: # Success
        print prompt + "Voicing " + target + " on channel " + chan
        voice(target,chan)

def voice(nick,chan):
  ircsock.send("MODE " + chan + " +v " + nick + '\n')

          #DEVOICE

def devoiceCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !devoice outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!devoice")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to devoice
        sendChanMsg(chan, "Bad arguments. Usage: !devoice <nick>")
      elif target != botnick: # Success
        print prompt + "Devoicing " + target + " on channel " + chan
        devoice(target,chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def devoice(nick,chan):
  ircsock.send("MODE " + chan + " -v " + nick + '\n')

          #OP

def opCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !op outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!op")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to op
        sendChanMsg(chan, "Bad arguments. Usage: !op <nick>")
      else: # Success
        print prompt + "Giving op to " + target + " on channel " + chan
        op(target,chan)

def op(nick,chan):
  ircsock.send("MODE " + chan + " +o " + nick + '\n')

          #DEOP

def deopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !deop outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!deop")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to deop
        sendChanMsg(chan, "Bad arguments. Usage: !deop <nick>")
      elif target != botnick: # Success
        print prompt + "Taking op from " + target + " on channel " + chan
        deop(target,chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def deop(nick,chan):
  ircsock.send("MODE " + chan + " -o " + nick + '\n')

          #HOP

def hopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !hop outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!hop")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to hop
        sendChanMsg(chan, "Bad arguments. Usage: !hop <nick>")
      else: # Success
        print prompt + "Giving hop to " + target + " on channel " + chan
        hop(target,chan)

def hop(nick,chan):
  ircsock.send("MODE " + chan + " +h " + nick + '\n')

          #DEHOP

def dehopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !dehop outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!dehop")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to dehop
        sendChanMsg(chan, "Bad arguments. Usage: !dehop <nick>")
      elif target != botnick: # Success
        print prompt + "Taking hop from " + target + " on channel " + chan
        dehop(target,chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def dehop(nick,chan):
  ircsock.send("MODE " + chan + " -h " + nick + '\n')

          #TOPIC

def topicCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !topic outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!topic 1 2 3 test"
      topic = msg.split("!topic")[1].lstrip(' ')
      if not topic:
        print prompt + "New topic is empty"
        sendChanMsg(chan, "Bad arguments. Usage: !topic [<new topic>]")
      else:
        print prompt + nick + " changed " + chan + " 's topic to '" + topic + "' "
        changeTopic(chan, topic)

def changeTopic(chan, topic):
  ircsock.send("TOPIC " + chan + " :" + topic + '\n')

          #KICK

def kickCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !kick outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!kick")[1].lstrip(' ')
      if not target: # Checks if user inserted a nickname to kick
        sendChanMsg(chan, "Bad arguments. Usage: !kick <nick>")
      elif target == botnick:
        print prompt + nick + " tried to kick the bot!"
        sendChanMsg(chan, "Don't make me kick myself out " + nick + '!')
      else:
        print prompt + "Kicking " + target + " from " + chan
        kick(target,chan,0)

def kick(nick,chan,isRand):
  if isRand:
    sendChanMsg(chan, "Randomly kicking " + nick + " from " + chan)
    ircsock.send("KICK " + chan + ' ' + nick + " lol_butthurt\n")
  else:
    sendChanMsg(chan, "Kicking " + nick + " from " + chan)
    ircsock.send("KICK " + chan + ' ' + nick + " lol_butthurt\n")

          #RANDOM KICK

def randKick(nicks, chan):
  size = len(nicks) - 1 # Correcting offset (this means if we have an array with 5 elements we should pick a random number between 0 and 4)
  rand = random.randint(0,size) # Picks a random number
  if botnick not in nicks[rand]: # Prevents bot from being kicked by !randkick
    print prompt + "Randomly kicking " + nicks[rand].__str__() + " from channel " + chan
    kick (nicks[rand],chan,1)
  else:
    print prompt + "Bot will not be kicked. Picking another one..."
    randKick(nicks,chan)
    
          # IGNORE

def ignCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(':')[1]:
      target = msg.split(":!ign")[1].lstrip(' ')
      if target:
        ign(nick, target)

def ign(nick, target):
  global ignUsrs
  ignUsrs.append(target)
  with open("ign.txt", 'w') as f:
    for elem in ignUsrs:
      f.write("%s\n" % elem)
  f.closed
  sendNickMsg(nick, target + " ignored!")
  print prompt + "Ign -> " + ignUsrs.__str__()

          #DICE

def dice(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    dice = random.randint(1,6).__str__() # converts the integer dice to a string to be concatenated in the final output
    print prompt + nick + " rolled the dice and got a " + dice
    sendChanMsg(chan, nick + " rolled a " + dice)

          #QUOTES

def quoteCmd(msg): #TODO: quote IDs
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !quote outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!quote random"
      '''
      if not msg.split("!quote")[1] or not msg.split("!quote ")[1]:
        sendChanMsg(chan,"Bad arguments. Usage: !quote num/random")
      else:
        quoteNum = msg.split("!quote ")[1]
        if quoteNum == "random":
      '''
      global quotes
      line = random.choice(quotes)
      if line:
        author = line.split ("|!|")[0]
        quote = line.split ("|!|")[1]
        print prompt + author + '\n' + prompt + quote #debugging
        sendChanMsg(chan, "[Quote] " + quote)
      else:
        print prompt + "File quotes.txt is empty"
        sendChanMsg(chan, "There are no quotes on the DB. Could something be wrong???")

def addQuote(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]: # Checks if quote was sent outside of a channel
      print prompt + nick + " sent !addquote outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!quote random"
      newQuote = msg.split("!addquote")[1].lstrip(' ')
      if not newQuote: # Checks for empty quote
        sendChanMsg(chan,"Bad arguments. Usage: !addquote [<quote>]")
      else:
        global quotes
        quotes.append(nick + "|!|" + newQuote)
        print prompt + nick + " added '" + newQuote + "'\n"
        with open("quotes.txt", 'w') as f:
          for i in quotes:
            f.write("%s\n" % i)
        f.closed
        sendChanMsg(chan, "Quote added!")

          #BLUEBERRYFOX

def bbfquotes(msg): # blueberryfox's private function
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !blueberry outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      print prompt + "Sending blueberryfox's fav quotes to " + chan
      sendChanMsg (chan, "Blueberryfoxes favorite Quotes: One, two, three, four, I declare a thumb war, five, six, seven, eight I use this hand to masturbate")
      time.sleep(1)
      sendChanMsg (chan, "I was like ohho!")
      time.sleep(1)
      sendChanMsg (chan, "I love your hair")

          #GREET MESSAGES

def setGreetCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]: #let's make sure people use this privately so that people won't see the welcoming message until they join a channel
      chan = getChannel(msg)
      print prompt + nick + " sent !setjoinmsg in " + chan + ". Sending warning..."
      sendChanMsg(chan, "Don't do that in the channel " + nick)
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else:
      newMsg = msg.split(":!setjoinmsg")[1].lstrip(' ') # Retrieves the entry message
      if not newMsg: # Checks if entry message is empty
        setGreet(nick, newMsg, False) # if empty we send False to setGreet so the bot knows the user wants to unset his greet
      else:
        setGreet(nick, newMsg, True) # in this case the user wants to change or create an entry message so we send True

def setGreet(nick, newMsg, toSet):
  global greets
  changed = False
  for idx, content in enumerate(greets): # Here we start scanning the array
    if nick + "|!|" in content.__str__(): # In this case the user already has a greet message
      if toSet: # This will happen if there is a new entry message and not an empty one
        greets[idx] = nick + "|!|" + newMsg # Changes the entry message to the new one
        print prompt + "Resetting " + nick + "'s greet message to '" + newMsg + "' "
        sendNickMsg(nick, "Entry message re-set!")
        changed = True
        break # We've found the nickname we can get out of the loop
      else: # This will happen if there is an empty entry message on an existing nick
        greets[idx] = None # Completely erases the content
        greets.remove(None)
        print prompt + "Unsetting " + nick + "'s greet message"
        sendNickMsg(nick, "Entry message unset!")
        changed = True
        break # We've found the nickname we can get out of the loop
  if toSet and not changed: # this will happen if there is a message and we didn't find a nickname in the file which means it's the 1st time being used or it was erased previously
        greets.append(nick + "|!|" + newMsg) # Adds the nick and corresponding greet message
        print prompt + "Setting " + nick + "'s greet message to '" + newMsg + "' "
        sendNickMsg(nick, "Entry message set!")
  with open("greet.txt", 'w') as f:
    for i in greets:
      f.write("%s\n" % i)
  f.closed # Closes the file to save resources
  
def sendGreet(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    # ":b0nk!LoC@fake.dimension JOIN #test"
    chan = msg.split(" JOIN ")[1]
    greet = ''
    global greets
    for elem in greets:
      if nick + "|!|" in elem:
        greet = elem.split("|!|")[1]
        print prompt + "Greeting " + nick + " in " + chan
        break
    if greet:
      sendChanMsg(chan, greet)
  
          #PART MESSAGES
  
def setPartCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]: #let's make sure people use this privately so that people won't see the part message until they leave a channel
      chan = getChannel(msg)
      print prompt + nick + " sent !setquitmsg in " + chan + ". Sending warning..."
      sendChanMsg(chan, "Don't do that in the channel " + nick)
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else:
      newMsg = msg.split(":!setquitmsg")[1].lstrip(' ') # Retrieves the part message
      if not newMsg: # Checks if part message is empty
        setPart(nick, newMsg, False) # if empty we send False to setPart so the bot knows the user wants to unset his part message
      else:
        setPart(nick, newMsg, True) # in this case the user wants to change or create an entry message so we send True

def setPart(nick, newMsg, toSet):
  global parts
  changed = False
  for idx, content in enumerate(parts): # Here we start scanning the array
    if nick + "|!|" in content.__str__(): # In this case the user already has a part message
      if toSet: # This will happen if there is a new part message and not an empty one
        parts[idx] = nick + "|!|" + newMsg # Changes the part message to the new one
        print prompt + "Resetting " + nick + "'s part message to '" + newMsg + "' "
        sendNickMsg(nick, "Part message re-set!")
        changed = True
        break # We've found the nickname we can get out of the loop
      else: # This will happen if there is an empty entry message on an existing nick
        parts[idx] = None # Completely erases the content
        parts.remove(None)
        print prompt + "Unsetting " + nick + "'s part message"
        sendNickMsg(nick, "Part message unset!")
        changed = True
        break # We've found the nickname we can get out of the loop
  if toSet and not changed: # this will happen if there is a message and we didn't find a nickname in the file which means it's the 1st time being used or it was erased previously
        parts.append(nick + "|!|" + newMsg) # Adds the nick and corresponding part message
        print prompt + "Setting " + nick + "'s part message to '" + newMsg + "' "
        sendNickMsg(nick, "Part message set!")
  with open("part.txt", 'w') as f:
    for i in parts:
      f.write('%s\n' % i)
  f.closed # Closes the file to save resources
  
def sendPart(msg, isQuit):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    # ":b0nk!~LoC@fake.dimension PART #test :FGSFDS"
    # ":steurun!~androirc@r3if800ykeveolu-mmuluxhgxm QUIT :Ping timeout: 260 seconds"
    global parts
    part = ''
    for elem in parts:
      if nick + "|!|" in elem:
        part = elem.split("|!|")[1]
        print prompt + "Saying goodbye to " + nick + "..."
        break
    if part and isQuit: # Bot says goodbye when the user leaves the network
      sendChanMsg("#boxxy", part)
    elif part and not isQuit: # Bot says goodbye when the user leaves the channel
      chan = msg.split(" PART ")[1].split(' ')[0]
      sendChanMsg(chan, part)
  
          #TAG (play catch)
          
def startTag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]: # Checks of command was sent in a channel
      print prompt + nick + " sent !starttag outside of a channel" #debugging
      sendNickMsg(nick, "You are not in a channel") # Warned the nickname
    else:
      global isTagOn, tagged
      chan = getChannel(msg) # Get the channel where the game is taking place
      if not isTagOn: # Checks if a game is in progress
        tagged = nick # Whoever starts the game is it
        isTagOn = True # Set game start
        sendChanMsg(chan, "The game starts and " + nick + " is it!")
      else: # Warns if game is on progress
        sendChanMsg(chan, "A game is already in progress.")
    
def endTag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !endtag outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      global isTagOn, tagged
      chan = getChannel(msg)
      if isTagOn:
        isTagOn = False
        tagged = ''
        sendChanMsg(chan, "The fun is over people :( it's raining...")
      else:
        sendChanMsg(chan, "There is no game in progress!")
          
def tag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !tag outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      global isTagOn, tagged, prevTagged
      if isTagOn:
        target = msg.split("!tag")[1].lstrip(' ')
        if not target: # Checks if the nick tagged nothing
          sendChanMsg(chan , "Tag who??? Usage: !tag <nick>")
        else:
          target = target.rstrip(' ') # Removes trailing spaces left by some clients auto-complete
          if target in list(taggers): # Target must exist in the list of players
            if nick == tagged: # Checks if the player is it
              if nick == target: # Checks if player is tagging himself
                print prompt + nick + " tagged himself"
                sendChanMsg(chan, "Don't tag yourself " + nick)
              elif target == botnick: # Checks if the bot gets tagged
                print prompt + nick + " tagged the bot!"
                sendChanMsg(chan, nick + " tagged me!")
                target = random.choice(list(taggers)) # Bot picks a random player to tag
                print prompt + "Tagging " + target + "..."
                tagged = target
                sendChanMsg(chan, target + " Tag! You're it!")
                prevTagged = nick
              else: # Player tags someone other than himself or the bot
                print prompt + tagged + " tagged " + target
                tagged = target
                prevTagged = nick
                sendChanMsg(chan, nick + " tagged you " + target + " you're it!")
            else:
              sendChanMsg(chan, nick + " you are not it!")
          else:
            sendChanMsg(chan, "Who are you tagging " + nick + "? Maybe " + target + " was not here when the game started.")
      else:
        sendChanMsg(chan, nick + " we're not playing tag now...")

def setTagged(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !settagged outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      global isTagOn, prevTagged, tagged
      if isTagOn:
        target = msg.split("!settagged")[1].lstrip(' ')
        if not target: # Checks if the nick wrote anything to set
          sendChanMsg(chan , "Set who??? Usage: !settagged <nick>")
        else:
          target = target.rstrip(' ') # Removes trailing spaces left by some clients auto-complete
          if target in list(taggers): # Target must exist in the list of players
            if nick == prevTagged:
              if nick == target:
                print prompt + nick + " set himself as tagged"
                sendChanMsg(chan, "Don't tag yourself " + nick)
              elif target == botnick:
                print prompt + nick + " set the bot as tagged!"
                sendChanMsg(chan, nick + " tagged me instead!")
                target = random.choice(list(taggers)) # Bot picks a random player to tag
                print prompt + "Tagging " + target + "..."
                tagged = target
                sendChanMsg(chan, target + " Tag! You're it!")
              else:
                print prompt + nick + " decided to tag " + target + " instead"
                sendChanMsg(chan, nick + " decided to tag " + target + " instead")
                tagged = target
                sendChanMsg(chan, nick + " tagged you " + target + " you're it!")
            else:
              sendChanMsg(chan, nick + " you were not previously it.")
          else:
            sendChanMsg(chan, "Who are you tagging " + nick + "? Maybe " + target + " was not here when the game started.")
      else:
        sendChanMsg(chan, nick + " we're not playing tag now...")
      
          #ROSE
          
def rose(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !rose outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!rose")[1].lstrip(' ')
      if not target: # Checks for a target to send a rose to
        sendChanMsg(chan , nick + " don't keep the roses to yourself. Usage: !rose <nick>")
      else:
        target = target.rstrip(' ')
        if nick == target: # Checks if nick is sending a rose to himself
          print prompt + nick + " is being selfish with the roses"
          sendChanMsg(chan, "Don't be selfish " + nick + " give that rose someone else")
        elif target == botnick:
          print prompt + nick + " sent a rose to the bot."
          sendChanMsg(chan, nick + " gave me a rose!")
          sendChanMsg(chan, '[' + nick + ']' + ' ' + rosestr + ' ' + '[' + target + ']')
          sendChanMsg(chan, ":3 thanks 4<3")
        else: # Success (normal case)
          print prompt + nick + " sent a rose to " + target
          sendChanMsg(chan, nick + " gives a rose to " + target)
          sendChanMsg(chan, '[' + nick + ']' + ' ' + rosestr + ' ' + '[' + target + ']')
        
          #BOOBS
          
def boobs(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !boobs outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!boobs")[1].lstrip(' ')
      if not target: # Checks for a target to show boobs to
        sendChanMsg(chan , nick + " don't hide those boobs. Usage: !boobs <nick>")
      else:
        target = target.rstrip(' ')
        if nick == target: # Checks if nick is sending !boobs to itself
          print prompt + nick + " is being shy with those boobs"
          sendChanMsg(chan, "Stop looking at the mirror " + nick + " show us them boobs")
        elif target == botnick:
          print prompt + nick + " sent !boobs to the bot."
          sendChanMsg(chan, nick + " those are cute")
          sendChanMsg(chan, "But mine are bigger --> ( . Y . )")
        else: # Success (normal case)
          print prompt + nick + " sent !boobs to " + target
          sendChanMsg(chan, nick + " shows " + target + " some boobs")
          sendChanMsg(chan, '[' + nick + ']' + ' ' + boobsstr + ' ' + '[' + target + ']')
        
          #SAY
          
def sayCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      print prompt + nick + " sent !say in " + chan + ". Sending warning..."
      sendChanMsg(chan, "Don't do that in the channel " + nick)
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else: # ":b0nk!~LoC@fake.dimension PRIVMSG testbot :!say #boxxy lol message"
      target = msg.split(':')[2].split(' ')[1]
      message = msg.split(target)[1].lstrip(' ')
      ircsock.send("PRIVMSG " + target + " :" + message + '\n')
    
          #8BALL
          
def eightBallCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !8ball outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      question = msg.split(':!8ball')[1].lstrip(' ')
      if not question or '?' not in question:
        print prompt + nick + " didn't ask a question"
        sendChanMsg(chan, "How about you ask me a question properly " + nick + "? Usage !8ball [<question>]?")
      else:
        global eightball
        answer = random.choice(eightball)
        if answer:
          print prompt + "8ball says: " + answer
          sendChanMsg(chan, nick + " asked [" + question + "] the 8ball says: " + answer)
        else:
          print prompt + "No 8ball answers"
          sendChanMsg(chan, "No 8ball answers :(")
        
          #LAST.FM
          
def getLfmUser(nick): # this looks for the last.fm username by nick
  global lfmUsers
  user = ''
  for i in lfmUsers:
    if nick in i:
      user = i.split('|!|')[1]
  return user #returns empty if not found


def setLfmUserCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    lfm_username = msg.split(":.setuser")[1].lstrip(' ')
    if not lfm_username:
      setLfmUser(nick, lfm_username, False) #sends false flag to unset username
    else:
      setLfmUser(nick, lfm_username, True) #sends true flag to set/re-set username


def setLfmUser(nick, lfm_username, toSet):
  global lfmUsers
  changed = False # hit detection
  for idx, content in enumerate(lfmUsers): # scans array
    if nick + "|!|" in content.__str__(): # finds the nickname
      if toSet:
        lfmUsers[idx] = nick + "|!|" + lfm_username
        print prompt + nick + " re-set it's LAST.FM username to " + lfm_username
        sendNickMsg(nick, "last.fm username re-set!")
        changed = True
        break # get out of loop
      else:
        lfmUsers[idx] = None
        lfmUsers.remove(None)
        print prompt + nick + " unset it's LAST.FM username"
        sendNickMsg(nick, "last.fm username unset!")
        changed = True
        break
  if toSet and not changed:
        lfmUsers.append(nick + "|!|" + lfm_username)
        print prompt + nick + " set it's LAST.FM username to " + lfm_username
        sendNickMsg(nick, "last.fm username set!")
  with open("lfmusers.txt", 'w') as f:
    for i in lfmUsers:
      f.write('%s\n' % i) # stores data back to file
  f.closed


def compareLfmUsers(msg): # use of the last.fm interface (pylast) in here
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent .compare outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      args = msg.split(':')[2].rstrip(' ').split(' ') # puts usernames in array
      if args.__len__() == 3: # correct usage
        user_name1 = args[1] # assigning usernames to vars
        user_name2 = args[2]
        global lastfm
        try:
          compare = lastfm.get_user(user_name1).compare_with_user(user_name2, 5) # comparison information from pylast
        except pylast.WSError as e: # One or both users do not exist
          print prompt + e.details
          sendChanMsg(chan, lfm_logo + "Error: " + e.details.__str__())
          return None
        global cmp_bars
        index = round(float(compare[0]), 4)*100 # compare[0] contains a str with a num from 0-1 here we round it to 4 digits and turn it to a percentage 0-100
        if index < 1.0:
          bar = cmp_bars[4]
        else:
          bar = cmp_bars[int(index / 25.0001)] # int(index / 25.0001) will return an integer from 0 to 3 to choose what bar to show
        raw_artists = []
        raw_artists = compare[1] # compare[1] contains and array of pylast.artist objects
        artist_list = ''
        if raw_artists.__len__() > 0: # users have artists in common
          while raw_artists:
            artist_list += raw_artists.pop().get_name().encode('utf8') + ", " # artist list string is built
          artist_list = artist_list.rstrip(", ")
        else: # no artists in common so we return '(None)'
          artist_list = "(None)"
        sendChanMsg(chan, lfm_logo + "Comparison: " + user_name1 + ' ' + bar + ' ' + user_name2 + " - Similarity: " + index.__str__() + "% - Common artists: " + artist_list)
        print prompt + "Comparison between " + user_name1 + " and " + user_name2 + ' | ' + index.__str__() + "% | " + artist_list
      else:
        print prompt + nick + " sent bad arguments for .compare"
        sendChanMsg(chan, lfm_logo + "Bad arguments! Usage: .compare <username1> [username2]") # warning for bad usage


def nowPlaying(msg): # use of the last.fm interface (pylast) in here
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent .np outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split(":.np")[1].lstrip(' ')
      if not target: # let's check the file
        target = getLfmUser(nick)
      if not target: # he is not in the db
        sendChanMsg(chan , lfm_logo + "First set your username with .setuser <last.fm username>. Alternatively use .np <last.fm username>")
        print prompt + nick + " sent .np but is not registered"
      else:
        global lastfm
        lfm_user = lastfm.get_user(target) # returns pylast.User object
        try: # some random fuction to raise exception if the user does not exist
          lfm_user.get_id()
        except pylast.WSError as e: # catched the exception, user truly does not exist
          print e.details
          sendChanMsg(chan, lfm_logo + "Error: " + e.details.__str__())
          return None # GTFO
        if lfm_user.get_playcount().__int__() < 1: # checks if user has scrobbled anything EVER
          sendChanMsg(chan, lfm_logo + target + " has an empty library")
          print prompt + target + " has an empty library" # no need to get a nowplaying when the library is empty
        else:
          np = lfm_user.get_now_playing() # np is now a pylast.Track object
          if np is None: # user does not have a now listening track
            sendChanMsg(chan, lfm_logo + target + " does not seem to be playing any music right now...")
            print prompt + target + " does not seem to be playing any music right now..."
          else: # all went well
            artist_name = np.artist.get_name().encode('utf8')# string containing artist name
            track = np.title.encode('utf8') #string containing track title
            
            try: # here we check if the user has ever played the np track
              playCount = int(np.get_add_info(target).userplaycount)
            except (ValueError, TypeError): #this error means track was never played so we just say it's 1
              playCount = 1
            
            np = np.get_add_info(target)
            
            if np.userloved == '1': # checks if np is a loved track to show when brodcasted to channel
              loved = " 4<3"
            else:
              loved = ''
            
            raw_tags = np.get_top_tags(5)
            if raw_tags.__len__() < 1: # some tracks have no tags therefor we request the artist tags
              raw_tags = np.artist.get_top_tags(5)
            tags = ''
            while raw_tags:
              tags += raw_tags.pop().item.name.encode('utf8') + ", " # builds tags string
            tags = tags.rstrip(", ") # removes last comma
            
            sendChanMsg(chan, lfm_logo + target + " is now playing: " + artist_name + " - " + track + "" + loved + " (" + playCount.__str__() + " plays, " + tags + ")")# broadcast to channel
            print prompt + target + " is now playing: " + artist_name + " - " + track + loved + " (" + playCount.__str__() + " plays, " + tags + ")"
              #last.fm | b0nk is now playing: Joan Jett and the Blackhearts - You Want In, I Want Out (1 plays, rock, rock n roll, Joan Jett, 80s, pop)
    

          #TWITTER
          
def getTweet(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(':')[1]:
      print prompt + nick + " sent !twitter outside of a channel"
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      arg = msg.split(":!twitter")[1].lstrip(' ')
      if arg:
        t_user = arg.translate(None, '@')
        index = 0
        if ' ' in arg:
          t_user = arg.split(' ')[0]
          index = arg.split(' ')[1]
          try:
            index = int(index)
          except ValueError:
            index = 0
        global t_api
        try:
          tweets = t_api.GetUserTimeline(None, t_user)
          tweet = tweets[index].GetText().encode('utf8')
          t_user = t_api.GetUser(None, t_user)._screen_name.encode('utf8')
          sendChanMsg(chan, t_logo + '@' + t_user + ': ' + tweet)
          print prompt + t_user + ' ' + index.__str__() + ' ' + tweet
        except twitter.TwitterError as e:
          err_msg = e.message[0].get('message').encode('utf8')
          err_code = e.message[0].get('code').__str__()
          print err_msg + ' Code:' + err_code
          sendChanMsg(chan, t_logo + "Error: " + err_msg + ' Code:' + err_code)
          return None # GTFO
      else:
        print prompt + nick + " used bad arguments for !twitter"
        sendChanMsg(chan, t_logo + "Bad arguments! Usage: !twitter <twitteruser> [optional number]")

          #QUIT

def quitIRC(): #This kills the bot!
  print prompt + "Killing the bot..."
  ircsock.send("QUIT " + quitmsg + '\n')

      #HELP (THE WALL OF TEXT) keep this on the bottom

def helpcmd(msg): #Here is the help message to be sent as a private message to the user
  nick = getNick(ircmsg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    print prompt + "Help requested by " + nick
    sendNickMsg(nick, "You have requested help.")
    time.sleep(0.5) # 0.5 seconds to avoid flooding
    sendNickMsg(nick, "You can say \'Hello " + botnick + "\' in a channel and I will respond.")
    time.sleep(0.5)
    sendNickMsg(nick, "You can also invite me to a channel and I'll thank you for inviting me there.")
    time.sleep(0.5)
    sendNickMsg(nick, "General commands: !help !invite !rtd !quote !addquote !setjoinmsg !setquitmsg !starttag !endtag !tag !rose !boobs !8ball !pass")
    time.sleep(0.5)
    sendNickMsg(nick, lfm_logo + "commands: .setuser .np .compare")
    time.sleep(0.5)
    sendNickMsg(nick, t_logo + "commands: !twitter")
    time.sleep(0.5)
    #sendNickMsg(nick, g_logo + " commands: !google")
    #time.sleep(0.5)
    if nick in authUsrs:
      sendNickMsg(nick, "Channel control commands: !op !deop !hop !dehop !voice !devoice !topic !kick !randkick")
      time.sleep(0.5)
    sendNickMsg(nick, "I've been written in python 2.7 and if you want to contribute or just have an idea, talk to b0nk on #test .")

# Initializations TODO:

loadAuth()
loadIgn()
loadGreets()
loadParts()
loadQuotes()
load8ball()
loadLfmUsers()
loadLfm()
loadTwitter()

# Connection
try:
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TODO: IPv6 ???
  ircsock = ssl.wrap_socket(ircsock) # SSL wrapper for the socket
  ircsock.connect((server, ssl_port)) # Here we connect to the server using the port defined above
  ircsock.send("USER " + botuser + ' ' + bothost + ' ' + botserver + ' ' + botname + '\n') # Bot authentication
  time.sleep(3)
  identify() # Bot identification
  time.sleep(3)
  joinChans(chans)
  time.sleep(3)
  idleRPG()

  while 1: # This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
    ircmsg = ircsock.recv(1024) # Receive data from the server
    ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
    print ircmsg # Here we print what's coming from the server
    
    if "PING :" in ircmsg: # If the server pings us then we've got to respond!
      reply = ircmsg.split("PING :")[1] # In some IRCds it is mandatory to reply to PING the same message we recieve
      ping(reply)
      
    if " 353 " in ircmsg:
      try:
        # ":irc.catiechat.net 353 testbot = #test :KernelPone ~b0nk CommVenus @testbot " 
        chan = ircmsg.split(" = ")[1].split(' ')[0]
        ircmsg = ircmsg.split(':')[2] # Returns raw list of nicks
        ircmsg = ircmsg.translate(None, '~@+&%') # Removes user mode characters
        ircmsg = ircmsg.rstrip(' ') # Removes an annoying SPACE char left by the server at the end of the string
        ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
        nicks = ircmsg.split(' ') # Puts nicks in an array
        print prompt + nicks.__str__() # debugging
        if botnick not in list(nicks):
          ircsock.send("NAMES " + chan + '\n')
        
        # Now that we have the nicks we can decide what to do with them depending on the command
        if "!randkick" in lastCommand:
          lastCommand = ''
          randKick(nicks, chan)
        
        if "!starttag" in lastCommand:
          lastCommand = ''
          if not isTagOn:
            taggers = nicks
            startTag(tmpstr)
            tmpstr = ''
          else:
            sendChanMsg(chan, "The game is already in progress!")
      except IndexError:
        print prompt + "Something went wrong..."
    
    if " INVITE " + botnick + " :" in ircmsg:
      tmpstr = ircmsg
      # :testbot!~I@m.botxxy.you.see INVITE b0nk :#test
      nick = getNick(tmpstr)
      if nick not in ignUsrs:
        target = tmpstr.split(':')[2]
        print prompt + nick + " invited the bot to " + target + ". Joining..."
        joinChan(target)
        sendChanMsg(target, "Thank you for inviting me here " + nick + '!')
        tmpstr = ''
    
    if ":hello " + botnick in ircmsg.lower() or ":hi " + botnick in ircmsg.lower(): # If we can find "Hello/Hi testbot" it will call the function hello(nick)
      hello(ircmsg)
      
    if ":!help" in ircmsg: # checks for !help
      helpcmd(ircmsg)
    
    if ":!ident" in ircmsg:
      user = getUser(ircmsg)
      if user == "b0nk!~LoC@fake.dimension":
        identify()
      
    if ":!die" in ircmsg: #checks for !die
      user = getUser(ircmsg)
      if user == "b0nk!~LoC@fake.dimension": # TODO: use auth
        quitIRC()
        break
      else:
        nick = getNick(ircmsg)
        print prompt + nick + " tried to kill the bot. Sending warning..."
        sendNickMsg(nick, "I'm afraid I can't let you do that " + nick + "...")
      
    if ":!invite" in ircmsg:
      inviteCmd(ircmsg)
      
    if ":!voice" in ircmsg:
      voiceCmd(ircmsg)
      
    if ":!devoice" in ircmsg:
      devoiceCmd(ircmsg)
      
    if ":!op" in ircmsg:
      opCmd(ircmsg)
      
    if ":!deop" in ircmsg:
      deopCmd(ircmsg)
    
    if ":!hop" in ircmsg:
      hopCmd(ircmsg)
      
    if ":!dehop" in ircmsg:
      dehopCmd(ircmsg)
    
    if ":!kick" in ircmsg:
      kickCmd(ircmsg)
      
    if ":!rtd" in ircmsg:
      dice(ircmsg)
      
    if ":!randkick" in ircmsg:
      nick = getNick(ircmsg)
      if nick not in ignUsrs:
        if '#' not in ircmsg.split(':')[1]:
          sendNickMsg(nick, "You are not in a channel!")
        else:
          chan = getChannel(ircmsg)
          ircsock.send("NAMES " + chan + '\n')
          print prompt + "Getting NAMES from " + chan
          lastCommand = "!randkick"
      
    if ":!topic" in ircmsg:
      topicCmd(ircmsg)
    
    if ":!pass" in ircmsg:
      authCmd(ircmsg)
    
    if ":!quote" in ircmsg:
      quoteCmd(ircmsg)
      
    if ":!addquote" in ircmsg:
      addQuote(ircmsg)
      
    if ":!blueberry" in ircmsg: #this will broadcast all of blueberrys favorite quotes :3
      bbfquotes(ircmsg)
    
    if " JOIN " in ircmsg:
      sendGreet(ircmsg)
      
    if " PART " in ircmsg:
      sendPart(ircmsg, False)
      
    if " QUIT " in ircmsg:
      sendPart(ircmsg, True)
      
    if ":!setjoinmsg" in ircmsg:
      setGreetCmd(ircmsg)
      
    if ":!setquitmsg" in ircmsg:
      setPartCmd(ircmsg)
    
    if ":!tag" in ircmsg:
      tag(ircmsg)
      
    if ":!starttag" in ircmsg:
      nick = getNick(ircmsg)
      if nick not in ignUsrs:
        if '#' not in ircmsg.split(':')[1]:
          sendNickMsg(nick, "You are not in a channel!")
        else:
          chan = getChannel(ircmsg)
          ircsock.send("NAMES " + chan + '\n')
          print prompt + "Getting NAMES from " + chan
          lastCommand = "!starttag"
          tmpstr = ircmsg
    
    if ":!endtag" in ircmsg:
      endTag(ircmsg)
      
    if ":!settagged" in ircmsg:
      setTagged(ircmsg)
      
    if ":!rose" in ircmsg:
      rose(ircmsg)
      
    if ":!boobs" in ircmsg:
      boobs(ircmsg)
      
    if ":!say" in ircmsg:
      sayCmd(ircmsg)
      
    if ":!8ball" in ircmsg:
      eightBallCmd(ircmsg)
      
    if ":!ign" in ircmsg:
      ignCmd(ircmsg)
    
    if ":.np" in ircmsg:
      nowPlaying(ircmsg)
    
    if ":.setuser" in ircmsg:
      setLfmUserCmd(ircmsg)
      
    if ":.compare" in ircmsg:
      compareLfmUsers(ircmsg)
      
    '''
    if "!google" in ircmsg:
      gSearch(ircmsg)
    '''
      
    if "!twitter" in ircmsg:
      getTweet(ircmsg)
    
except socket.error as e:
  print e.strerror
  print prompt + "Bot timedout / killed???"
