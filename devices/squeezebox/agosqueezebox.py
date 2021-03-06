#!/usr/bin/env python

# Squeezebox client
# copyright (c) 2013 tang
 
import sys
import agoclient
import pylmsserver
import pylmsplaylist
import pylmslibrary
import threading
import time
import logging

host = ''
server = None
playlist = None
library = None
client = None
states = {}
mediastates = {}

STATE_OFF = 0
STATE_ON = 255

STATE_STREAM = 'streaming'
STATE_PLAY = 'play'
STATE_STOP = 'stopped'
STATE_PAUSE = 'paused'

#logging.basicConfig(filename='agosqueezebox.log', level=logging.INFO, format="%(asctime)s %(levelname)s : %(message)s")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s : %(message)s")

#utils
def getPlayer(player_id):
    """Return player according to player_id"""
    return playlist.get_server().get_player(player_id)
def getPlayers():
    """Return all players"""
    return playlist.get_server().get_players()

def quit(msg):
    """Exit application"""
    global playlist
    global client
    if playlist:
        playlist.stop()
        playlist = None
    if client:
        del client
        client = None
    logging.fatal(msg)
    sys.exit(0)

#squeezebox callbacks
def play_callback(player_id, track_title, playlist_index):
    #if player is off or player is already playing, kick this callback
    logging.info('callback PLAY: %s' % player_id)
    if mediastates.has_key(player_id) and mediastates[player_id]!=STATE_PLAY and mediastates[player_id]!=STATE_STREAM:
        mediastates[player_id] = STATE_PLAY
        emit_play(player_id)
def stop_callback(player_id):
    #if player is off, kick this callback
    logging.info('callback STOP: %s' % player_id)
    if mediastates.has_key(player_id) and mediastates[player_id]!=STATE_STREAM:
        mediastates[player_id] = STATE_STOP
        emit_stop(player_id)
def pause_callback(player_id):
    #if player is off, kick this callback
    logging.info('callback PAUSE: %s' % player_id)
    if mediastates.has_key(player_id) and mediastates[player_id]!=STATE_STREAM:
        mediastates[player_id] = STATE_PAUSE
        emit_pause(player_id)
def on_callback(player_id):
    logging.info('callback ON: %s' % player_id)
    if mediastates.has_key(player_id) and mediastates[player_id]!=STATE_STREAM:
        states[player_id] = STATE_ON
        emit_on(player_id)
def off_callback(player_id):
    logging.info('callback OFF: %s' % player_id)
    if mediastates.has_key(player_id) and mediastates[player_id]!=STATE_STREAM:
        states[player_id] = STATE_OFF
        emit_off(player_id)


#emit function
def emit_play(internalid):
    client.emitEvent(internalid, "event.mediaplayer.statechanged", "play", "")
    client.emitEvent(internalid, "event.device.mediastatechanged", str(STATE_PLAY), "")
def emit_stop(internalid):
    client.emitEvent(internalid, "event.mediaplayer.statechanged", "stop", "")
    client.emitEvent(internalid, "event.device.mediastatechanged", str(STATE_STOP), "")
def emit_pause(internalid):
    client.emitEvent(internalid, "event.mediaplayer.statechanged", "pause", "")
    client.emitEvent(internalid, "event.device.mediastatechanged", str(STATE_PAUSE), "")
def emit_on(internalid):
    client.emitEvent(internalid, "event.device.statechanged", str(STATE_ON), "")
def emit_off(internalid):
    client.emitEvent(internalid, "event.device.statechanged", str(STATE_OFF), "")
def emit_stream(internalid):
    client.emitEvent(internalid, "event.device.mediastatechanged", str(STATE_STREAM), "")

#init
try:
    #connect agoclient
    client = agoclient.AgoConnection("squeezebox")

    #read configuration
    host = agoclient.getConfigOption("squeezebox", "host", "127.0.0.1")
    port = int(agoclient.getConfigOption("squeezebox", "port", "9090"))
    login = agoclient.getConfigOption("squeezebox", "login", "")
    passwd = agoclient.getConfigOption("squeezebox", "password", "")
    logging.info("Config: %s@%s:%d" % (login, host, port))
    
    #connect to squeezebox server
    logging.info('Creating LMSServer...')
    server = pylmsserver.LMSServer(host, port, login, passwd)
    server.connect()
    
    #connect to notifications server
    logging.info('Creating LMSPlaylist...')
    library = pylmslibrary.LMSLibrary(host, port, login, passwd)
    playlist = pylmsplaylist.LMSPlaylist(library, host, port, login, passwd)
    #play, pause, stop, on, off, add, del, move, reload
    playlist.set_callbacks(play_callback, pause_callback, stop_callback, on_callback, off_callback, None, None, None, None)
    playlist.start()
    
except Exception as e:
    #init failed
    quit('Init failed, exit now. (%s)' % str(e))

    

#Set message handler
#state values:
# - 0 : OFF
# - 255 : ON
# - 25 : STREAM
# - 50 : PLAYING
# - 100 : STOPPED
# - 150 : PAUSED
def messageHandler(internalid, content):
    logging.info('messageHandler: %s, %s' % (internalid,content))

    #check parameters
    if not content.has_key("command"):
        logging.error('No command specified in content')
        return None

    if internalid==host:
        #server command
        if content["command"]=="allon":
            logging.info("Command ALLON: %s" % internalid)
            for player in getPlayers():
                player.on()
        elif content["command"]=="alloff":
            logging.info("Command ALLOFF: %s" % internalid)
            for player in getPlayers():
                player.off()
        elif content["command"]=="displaymessage":
            if content.has_key('line1') and content.has_key('line2') and content.has_key('duration'):
                logging.info("Command DISPLAYMESSAGE: %s" % internalid)
                for player in getPlayers():
                    player.display(content['line1'], content['line2'], content['duration'])
            else:
                logging.error('Missing parameters to command DISPLAYMESSAGE')
                return None
    else:
        #player command
        #get player
        player = getPlayer(internalid)
        if not player:
            logging.error('Player %s not found!' % internalid)
            return None
    
        if content["command"] == "on":
            logging.info("Command ON: %s" % internalid)
            player.on()
        elif content["command"] == "off":
            logging.info("Command OFF: %s" % internalid)
            player.off()
        elif content["command"] == "play":
            logging.info("Command PLAY: %s" % internalid)
            player.play()
        elif content["command"] == "pause":
            logging.info("Command PAUSE: %s" % internalid)
            player.pause()
        elif content["command"] == "stop":
            logging.info("Command STOP: %s" % internalid)
            player.stop()
        elif content["command"] == "displaymessage":
            if content.has_key('line1') and content.has_key('line2') and content.has_key('duration'):
                logging.info("Command DISPLAYMESSAGE: %s" % internalid)
                player.display(content['line1'], content['line2'], content['duration'])
            else:
                logging.error('Missing parameters to command DISPLAYMESSAGE')
                return None
client.addHandler(messageHandler)

#add server
client.addDevice(host, 'squeezeboxserver')

#add players
try:
    logging.info('Discovering players:')
    for p in server.get_players():
        logging.info("  Add player : %s[%s]" % (p.name, p.mac))
        client.addDevice(p.mac, "squeezebox")
except Exception as e:
    quit('Failed to discover players. Exit now. (%s)' % str(e))

#get players states
logging.info('Get current players states:')
try:
    for p in server.get_players():
        if p.get_model()=='http':
            #it's a stream. No control on it
            logging.info('  Player %s[%s] is a streaming' % (p.name, p.mac))
            states[p.mac] = STATE_ON
            mediastates[p.mac] = STATE_STREAM
            emit_stream(p.mac)
        elif not p.get_is_on():
            #player is off
            logging.info('  Player %s[%s] is off' % (p.name, p.mac))
            states[p.mac] = STATE_OFF
            mediastates[p.mac] = STATE_STOP
            emit_off(p.mac)
        else:
            #player is on
            mode = p.get_mode()
            states[p.mac] = STATE_ON
            if mode=='stop':
                logging.info('  Player %s[%s] is stopped' % (p.name, p.mac))
                mediastates[p.mac] = STATE_STOP
                emit_stop(p.mac)
            elif mode=='play':
                logging.info('  Player %s[%s] is playing' % (p.name, p.mac))
                mediastates[p.mac] = STATE_PLAY
                emit_play(p.mac)
            elif mode=='pause':
                logging.info('  Player %s[%s] is paused' % (p.name, p.mac))
                mediastates[p.mac] = STATE_PAUSE
                emit_pause(p.mac)
except Exception as e:
    quit('Failed to get player status. Exit now. (%s)' % str(e))

#run agoclient
try:
    logging.info('Running agosqueezebox...')
    client.run()
except:
    quit('agosqueezebox stopped')


