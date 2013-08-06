# https://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
# http://forum.codecall.net/topic/59608-developing-a-basic-irc-bot-with-python/
# http://docs.python.org/2/library/ssl.html
# http://docs.python.org/2/library/hashlib.html
# https://www.hackthissite.org/articles/read/1050
# http://stackoverflow.com/questions/4719438/editing-specific-line-in-text-file-in-python

'''
@author: b0nk
@version: 1.1.1
'''

# Import the necessary libraries.
import socket
import ssl
import hashlib
import time
import random
import string
import io

# Other imports
# Imports for last.fm methods
# https://code.google.com/p/pylast/
from random import choice
import pylast

# Imports for google search
#import urllib
#import json



# Some basic variables used to configure the bot

server = "boxxybabee.catiechat.net" # EU server
#server = "anewhopeee.catiechat.net" # US server
#server = "192.168.1.35"
port = 6667 # default port
ssl_port = 6697 # ssl port
chans = ["#test", ] #default channels
botnick = "GLaBOT" # bot nick
botuser = "GlaBOT"
bothost = "192.168.2.11"
botserver = "apzerver"
botname = "glabot"
botpassword = "tastycake"
quitmsg = "I hate you!"

# Global vars

nicks = []

authDB = []
authUsrs = []
ignUsrs = []
parts = []
taunts = []
quotes = []
cakeDeaths = []

lastCommand = ''
tmpstr = ''
rosestr = "3---<-<-{4@"
boobsstr = "(.Y.)"
cakestr_0 = "    _|||||_"
cakestr_1 = "   {~*~*~*~}"
cakestr_2 = " __{*~*~*~*}__ "
cakestr_3 = "`-------------`"
prompt = ">> "


#============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============

def myprint(msg):
    print "%s%s" % (prompt, msg)

def ping(reply): # This is our first function! It will respond to server Pings.
    ircsock.send("PONG :%s\n" % (reply)) # In some IRCds it is mandatory to reply to PING the same message we recieve
    #myprint("PONG :%s" % (reply))

def sendChanMsg(chan, msg): # This sends a message to the channel 'chan'
    ircsock.send("PRIVMSG %s :%s\n" % (chan, msg))

def sendNickMsg(nick, msg): # This sends a notice to the nickname 'nick'
    ircsock.send("NOTICE %s :%s\n" % (nick, msg))

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
    ircsock.send("JOIN %s\n" % (chan))

def joinChans(chans): # This is used to join all the channels in the array 'chans'
    for i in chans:
        ircsock.send("JOIN %s\n" % (i))

def hello(msg): # This function responds to a user that inputs "Hello testbot"
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        chan = getChannel(msg)
        myprint("%s said hi in %s" % (nick, chan))
        sendChanMsg(chan, "Hello, and again welcome to the Enrichment Centre, %s. Testing is available." % (nick))

def identify():
    ircsock.send("NICK %s\n" % (botnick)) # Here we actually assign the nick to the bot
    time.sleep(3)
    ircsock.send("NICKSERV IDENTIFY %s\n" % (botpassword)) # Identifies the bot's nickname with nickserv
    myprint("Bot identified")

#========================END OF BASIC FUNCTIONS=====================

#========================INITIALIZATIONS============================

# Ignores

def loadIgn():
    global ignUsrs
    ignUsrs = [line.strip() for line in open('ign.txt', 'r')]
    myprint("Ign -> %s" % (str(ignUsrs)))


# Parts

def loadParts():
    global parts
    parts = [line.strip() for line in open('part.txt', 'r')]
    myprint("Parts -> LOADED")

# Quotes

def loadQuotes():
    global quotes
    quotes = [line.strip() for line in open('quotes.txt', 'r')]
    myprint("Quotes -> LOADED")

# Cakes

def loadCakes():
    global cakeDeaths
    cakeDeaths = [line.strip() for line in open('cake.txt', 'r')]
    myprint("Cake -> LOADED")

# Taunts

def loadTaunts():
    global taunts
    taunts = [line.strip() for line in open('taunt.txt', 'r')]
    myprint("Taunt -> LOADED")

#=========================REMOTE CONTROL============================

def sayTemp(msg):
    chan = getChannel(msg)
    f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = float(f.readline())
    f.close()
    sendChanMsg(chan, 'Current CPU temperature is %d degrees Kelvin' % ((temp/1000)+273.15))


#===================================================================


#INVITE

def inviteCmd(msg): # Parses the message to extract NICK and CHANNEL
    # ":b0nk!LoC@fake.dimension PRIVMSG #test :!invite "
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        if '#' not in msg.split(':')[1]:
            myprint("%s sent !invite outside of a channel" % (nick))
            sendNickMsg(nick, "You are not in a channel")
        else:
            chan = getChannel(msg)
            target = msg.split("!invite")[1].lstrip(' ')
            if not target: # Checks if user inserted a nickname to invite
                sendChanMsg(chan, "Bad arguments. Usage: !invite <nick>")
            else: # Success
                myprint("Inviting %s to channel %s" % (target, chan))
                sendChanMsg(chan, "Inviting %s here..." % (target))
                invite(target, chan)

def invite(nick, chan): # Invites given nickname to present channel
    ircsock.send("INVITE " + nick + ' ' + chan + '\n')


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
    sendNickMsg(nick, "%s ignored!" % (target))
    myprint("Ign -> %s" % (str(ignUsrs)))


    #QUOTES

def quoteCmd(msg): #TODO: quote IDs
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        if '#' not in msg.split(':')[1]:
            myprint("%s sent !quote outside of a channel" % (nick))
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
                myprint(author + "%s" % (author)) #debugging
                myprint("%s" % (quote)) #debugging
                sendChanMsg(chan, "[Quote] %s" % (quote))
            else:
                myprint("File quotes.txt is empty")
                sendChanMsg(chan, "There are no quotes on the DB. Could something be wrong???")

def addQuote(msg):
    nick = getNick(msg)
    global ignUsrs, authUsrs
    if nick not in ignUsrs:
        if '#' not in msg.split(':')[1]: # Checks if quote was sent outside of a channel
            myprint("%s sent !addquote outside of a channel" % (nick))
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
                myprint("%s added '%s'" % (nick, newQuote))
                with open("quotes.txt", 'w') as f:
                    for i in quotes:
                        f.write("%s\n" % i)
                f.closed
                sendChanMsg(chan, "Quote added!")


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
                myprint("Saying goodbye to %s..." % (nick))
                break
        if part and isQuit: # Bot says goodbye when the user leaves the network
            sendChanMsg("#boxxy", part)
        elif part and not isQuit: # Bot says goodbye when the user leaves the channel
            chan = msg.split(" PART ")[1].split(' ')[0]
            sendChanMsg(chan, part)


            #CAKE

'''
  this function actually prints the cake, since it's a multi-line
  ascii art thing and i didn't want to rewrite its code everywhere
'''
def printCake(chan):
    sendChanMsg(chan, cakestr_0)
    sendChanMsg(chan, cakestr_1)
    sendChanMsg(chan, cakestr_2)
    sendChanMsg(chan, cakestr_3)

def cake(msg):
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        if '#' not in msg.split(':')[1]:
            myprint("%s sent !glacake outside of a channel" % (nick))
            sendNickMsg(nick, "You are not in a channel")
        else:
            chan = getChannel(msg)
            target = msg.split("!glacake")[1].lstrip(' ')
            if not target: # Checks for a target to promise some cake
                sendChanMsg(chan, "%s, there is science to do. Usage: !glacake <nick>" % (nick))
            else:
                target = target.rstrip(' ')
                if nick == target: # Checks if nick is eating the cake by himself
                    myprint("%s is tricking test subjects and eating the cake" % (nick))
                    sendChanMsg(chan, "Those test subjects won't test for free! %s, leave some cake for them" % (nick))
                elif target == botnick:
                    myprint("%s gives some tasty cake to the bot." % (nick))
                    printCake(chan)
                    sendChanMsg(chan, "Thank you %s!" % (nick))
                    sendChanMsg(chan, "It's so delicious and moist.")
                else: # Success (normal case)
                    myprint("%s is sharing some cake" % (nick))
                    sendChanMsg(chan, "I'm afraid testbot has control of all of the cake.")

                    #TAUNTS

def sayTaunt(msg):
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        if '#' not in msg.split(':')[1]:
            myprint("%s sent !glataunt outside of a channel" % (nick))
            sendNickMsg(nick, "You are not in a channel")
        else:
            chan = getChannel(msg)
            target = msg.split("!glataunt")[1].lstrip(' ')
            if not target: # Checks for a target to promise some cake
                sendChanMsg(chan, "I expected more from you, %s. Usage: !glataunt <nick>" % (nick))
            else:
                ta = choice(taunts)
                if len(ta.split("|!|")) == 2:
                    msg = "%s %s. %s %s" % (ta.split("|!|")[0], nick, target, ta.split("|!|")[1])
                elif ta.find("@") == 0:
                    msg = "%s %s" % (target, ta.strip("@"))
                else:
                    msg = "%s, %s" % (ta, target)

                sendChanMsg(chan, msg)


                    #SAY

def sayCmd(msg):
    nick = getNick(msg)
    global ignUsrs
    if nick not in ignUsrs:
        if '#' in msg.split(':')[1]:
            chan = getChannel(msg)
            myprint("%s sent !say in %s. Sending warning..." % (nick, chan))
            sendChanMsg(chan, "Don't do that in the channel %s" % (nick))
            sendNickMsg(nick, "Send it as a notice or query(pvt)")
        else: # ":b0nk!~LoC@fake.dimension PRIVMSG testbot :!say #boxxy lol message"
            target = msg.split(':')[2].split(' ')[1]
            message = msg.split(target)[1].lstrip(' ')
            ircsock.send("PRIVMSG %s :%s\n" % (target, message))


def sendGreet(msg):
    nick = getNick(msg).lower()
    chan = getChannel(msg)
    if nick.find("cave") >= 0 and nick.find("johnson") >=0:
        sendChanMsg(chan, "Hello, Mr. Johnson.")

    #QUIT

def quitIRC(): #This kills the bot!
    myprint("Killing the bot...")
    ircsock.send("QUIT " + quitmsg + '\n')

    #HELP (THE WALL OF TEXT) keep this on the bottom

def helpcmd(msg): #Here is the help message to be sent as a private message to the user
    nick = getNick(ircmsg)
    global ignUsrs, authUsrs
    if nick not in ignUsrs:
        myprint("Help requested by %s" % (nick))
        sendNickMsg(nick, "You have requested help.")
        time.sleep(0.5) # 0.5 seconds to avoid flooding
        sendNickMsg(nick, "You can say 'Hello %s' in a channel and I will respond." % (botnick))
        time.sleep(0.5)
        sendNickMsg(nick, "General commands: !glahelp !glatemp !glasay !glacake")
        time.sleep(0.5)
        sendNickMsg(nick, "I've been written in python 2.7 and I'm based on Botxxy, the friendly Bot by b0nk. Ask him about it.")

# Initializations TODO:

loadIgn()
loadParts()
loadQuotes()
loadCakes()
loadTaunts()

# Connection
try:
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TODO: IPv6 ???
    #ircsock = ssl.wrap_socket(ircsock) # SSL wrapper for the socket
    ircsock.settimeout(250.0)
    ircsock.connect((server, port)) # Here we connect to the server using the port defined above
    ircsock.send("USER %s %s %s %s\n" % (botuser, bothost, botserver, botname)) # Bot authentication
    identify() # Bot identification
    time.sleep(10)
    joinChans(chans)
    #  idleRPG()

    while 1: # This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
        ircmsg = ircsock.recv(1024) # Receive data from the server
        ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
        print ircmsg # Here we print what's coming from the server

        if "PING :" in ircmsg: # If the server pings us then we've got to respond!
            reply = ircmsg.split("PING :")[1] # In some IRCds it is mandatory to reply to PING the same message we recieve
            ping(reply)

        if " INVITE " + botnick + " :" in ircmsg:
            tmpstr = ircmsg
            # :testbot!~I@m.botxxy.you.see INVITE b0nk :#test
            nick = getNick(tmpstr)
            if nick not in ignUsrs:
                target = tmpstr.split(':')[2]
                myprint("%s invited the bot to %s. Joining..." % (nick, target))
                joinChan(target)
                sendChanMsg(target, "Thank you for inviting me here %s!" % (nick))
                tmpstr = ''

        if ":hello " + botnick.lower() in ircmsg.lower() or ":hi " + botnick.lower() in ircmsg.lower(): # If we can find "Hello/Hi testbot" it will call the function hello(nick)
            hello(ircmsg)

        if ":!glahelp" in ircmsg: # checks for !glahelp
            helpcmd(ircmsg)

        if ":!gladie" in ircmsg: #checks for !die
            user = getUser(ircmsg)
            if  user == "TheFerrango!~ferrango@labs.ferrangonet.com": # TODO: use auth
                quitIRC()
                break
            else:
                nick = getNick(ircmsg)
                myprint("%s tried to kill the bot. Sending warning..." % (nick))
                sendNickMsg(nick, "I'm afraid I can't let you do that " + nick + "...")

        if ":!glainvite" in ircmsg:
            inviteCmd(ircmsg)

        if ":!glaquote" in ircmsg:
            quoteCmd(ircmsg)

        if ":!glaaddquote" in ircmsg:
            addQuote(ircmsg)

        if " JOIN " in ircmsg:
            sendGreet(ircmsg)

        if " PART " in ircmsg:
            sendPart(ircmsg, False)

        if " QUIT " in ircmsg:
            sendPart(ircmsg, True)

        if ":!glacake" in ircmsg:
            cake(ircmsg)

        if ":!glasay" in ircmsg:
            sayCmd(ircmsg)

        if ":!glaign" in ircmsg:
            ignCmd(ircmsg)

        if ":!glatemp" in ircmsg:
            sayTemp(ircmsg)

        if ":!glataunt" in ircmsg:
            sayTaunt(ircmsg)

        #if "test" in ircmsg:
        #    print "Batman"

except socket.error as e:
    print e.strerror
    myprint("Bot killed / timedout")
