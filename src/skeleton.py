# https://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
# http://forum.codecall.net/topic/59608-developing-a-basic-irc-bot-with-python/

# Import the necessary libraries.
import socket
import ssl

# Some basic variables used to configure the bot

server = "boxxybabee.catiechat.net" # EU server
#server = "anewhopeee.catiechat.net" # US server
port = 6667 # default port
ssl_port = 6697 # ssl port
chans = ["#test", "#your_channels_here"] #default channels
botnick = "skeleton" # bot nick
botuser = "botuser"
bothost = "bothost"
botserver = "botserver"
botname = "botname"
botpassword = ""

# Global vars

prompt = '>> '

#============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============
	
def sendChanMsg(chan, msg): # This sends a message to the channel 'chan'
	ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")
	
def sendNickMsg(nick, msg): # This sends a notice to the nickname 'nick'
	ircsock.send("NOTICE " + nick + " :" + msg + "\n")
	
def getNick(msg): # Returns the nickname of whoever requested a command from a RAW irc privmsg. Example in commentary below.
	# ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
	return msg.split('!')[0].replace(':','')

def getChannel(msg): # Returns the channel from whereever a command was requested from a RAW irc PRIVMSG. Example in commentary below.
	# ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
	return msg.split(' PRIVMSG ')[-1].split(' :')[0]

def joinChan(chan): # This function is used to join a single channel.
	ircsock.send("JOIN " + chan + '\n')

def joinChans(chans): # This is used to join all the channels in the array 'chans'
	for i in chans:
		ircsock.send("JOIN " + i + '\n')

#========================END OF BASIC FUNCTIONS=====================

					#PING

def ping(reply): # This is our first function! It will respond to server Pings.
	ircsock.send("PONG :" + reply + "\n")

					#HELLO
					
def hello(msg): # This function responds to a user that inputs "Hello <botnick>"
	nick = getNick(msg)
	chan = getChannel(msg)
	print prompt + nick + " said hi in " + chan
	sendChanMsg(chan, "Hello " + nick)

# Connection

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock = ssl.wrap_socket(ircsock) # SSL wrapper for the socket
ircsock.connect((server, ssl_port)) # Here we connect to the server using the port defined above
ircsock.send("USER " + botuser + " " + bothost + " " + botserver + " " + botname + "\n") # Bot authentication
ircsock.send("NICK " + botnick + "\n") # Here we actually assign the nick to the bot
joinChans(chans)

while 1: # This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
	ircmsg = ircsock.recv(4096) # Receive data from the server
	ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
	print ircmsg # Here we print what's coming from the server
	
	if "PING :" in ircmsg: # If the server pings us then we've got to respond!
		reply = ircmsg.split("PING :")[1] # In some IRCds it is mandatory to reply to PING the same message we recieve
		ping(reply)
	
	if ":hello " + botnick in ircmsg.lower(): # If we can find "Hello botnick" it will call the function hello()
		hello(ircmsg)
	