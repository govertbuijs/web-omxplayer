#! /usr/bin/python

from bottle import static_file
from bottle import get, post, request
from bottle import route, run, template, redirect
from datetime import timedelta
from threading import Thread
from config import movie_location,omxoptions
import os, sys, urllib, omxplayer, config, time

player = None
playing_path = None
playing_file = None


@route('/img/<filename:path>')
def send_image(filename):
    return static_file(filename, root='./static/img', mimetype='image/png')


@route('/files/<filename:path>')
def send_image(filename):
    return static_file(filename, root='./static/files', 
            mimetype='application/vnd.android.package-archive')


@route('/css/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static/css', mimetype='text/css')


@route('/js/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static/js', mimetype='text/javascript')


@route('/files.ajax')
def files_ajax():
    try:
        def comparator(x,y):
            if x[0].upper() > y[0].upper():
                return 1
            if x[0].upper() < y[0].upper():
                return -1
            return 0
		
        if request.query.dr == None:
            dr = ''
        else:
            dr = urllib.unquote(request.query.dr)
	
        d = []
        f = []
        for i in os.listdir(urllib.unquote(movie_location+'/'+dr)):
            if os.path.isdir(urllib.unquote(movie_location+'/'+dr+"/"+i)):
                d.append([urllib.quote(i),i])
            else:
                if i.endswith((".srt", ".txt")):
                    continue
                f.append([urllib.quote(i),i])
        f.sort(comparator)
        d.sort(comparator)
        return template('files_ajax', dir_list=d,file_list=f,dr=urllib.quote(dr))
    except:
        return "<div class='folders'><div class='error'>" + \
                "Error accessing that folder: " + \
                str(sys.exc_info()[1]) + "</div></div>"


@route('/info.ajax')
def info():
    if request.query.file == None:
        return '00:00:00'

    ml = urllib.unquote(movie_location)
    fil = urllib.unquote(request.query.file)
    return omxplayer.file_info(ml+'/'+fil)


@route('/player.ajax')
def webplayer():
    global playing_path, playing_file
    if request.query.c != None:
        exec_command(request.query.c)

    #time.strftime('%H:%M:%S', time.gmtime(player.position))
 
    pos = None
    length = None
    try:
        position = timedelta(microseconds=max(0, player.position))
        pos = str(position).split('.')[0]
        if position.seconds < 6000:
            pos = '0' + pos
        length = player.duration
    except:
        pass
    
    return template('player_ajax', path = playing_path, 
            name = playing_file, pos = pos, length = length, 
            running = running())


@route('/')
def index():
    return template('index', dir_list = [], file_list = [], dr = '',
            path = playing_path, name = playing_file, running = running())


def exec_command(command):
    global player, playing_path, playing_file
    if command == 'pause' and player != None:
        player.toggle_pause()

    elif command == 'play':
        if player != None and player.is_running():
            exec_command('quit')

        ml = urllib.unquote(movie_location)
        fil = urllib.unquote(request.query.file)
        if check_input(ml, fil) == False:
            return None

        player = omxplayer.OMXPlayer(ml+fil, 
                                     omxoptions,
                                     start_playback=True,
                                     do_dict=True)
        #playing = ml+fil
        #print 'Playing: '+str(ml+fil)
        playing_path = '/'.join(fil.split('/')[0:-1])
        playing_file = fil.split('/')[-1]
        print
        print 'Playing: ' + playing_path +'/'+ playing_file
        print

    elif command == 'ahead' and player != None:
        player.skip_ahead()

    elif command == 'ahead2' and player != None:
        player.skip_ahead2()

    elif command == 'back' and player != None:
        player.skip_back()

    elif command == 'back2' and player != None:
        player.skip_back2()

    elif command == 'quit':
        if player != None:
            player.stop()
        player = None
        playing_path = None
        playing_file = None
	
    elif command == 'vol_up' and player != None:
        player.vol_up()

    elif command == 'vol_down' and player != None:
        player.vol_down()

    elif command == 'toggle_subs' and player != None:
        player.toggle_subtitles()


# check user input is OK
def check_input (videodir, track):
    if '.' in track:
        path = videodir + track
        if os.path.exists(path):
            return True
        else:
            print "File " + path + " not found"
            return False
    else:
        print track, " not understood"
        return False


def running():
    if player:
        return not player.paused
    else:
        return False


run(host='0.0.0.0', port=config.port)
