#!/usr/bin/env -S ../bin/python

import mido
import threading
from time import sleep

# global
sig_stop =     threading.Event()

class PlaybackServer:
    def __init__ (self, tcp_port=8100):
        self.tcp_port =     tcp_port
        self.clients =      dict()
        self.port =         self.init_output_port()
        self.exit_code =    self.start_server()

    def show_log (self, *args):
        print ("++++", *args)

    def init_output_port (self):
        ports = mido.get_output_names()

        self.show_log ("all ports:", ports)
        self.show_log ("using port /{}/ ...".format(ports[0]))

        mido.open_output(ports[0])

        self.show_log ("{} opened.".format(ports[0]))

        return ports[0]

    def accept_connection (self, client):
        self.show_log ('Connection from {}'.format(client.name))

        # spawn a thread to listen to events there
        thread = threading.Thread(target=self.client_instance, daemon=True, args=(client,))

        # map
        self.clients[client] = thread
        # OLD ( (thread, client) )
        self.show_log ('spawn thread for: {}'.format(client.name))

        return thread

    def process_message (self, message):

        # we dont want to send wrong datatypes to internal classes
        # (they will prolly whine)

        if not isinstance(message, mido.Message):
            raise Exception("message is not mido.Message!")

        # send the MIDI message to the output port
        with mido.open_output(self.port) as outport:
            self.show_log (message)
            outport.send(message)

            # OLD outport.send(mido.Message('note_on', note=60, velocity=100))
    #enddef

    def client_instance (self, client):
        self.show_log ('Running instance {}.'.format(client))

        # the closest thing we have to callbacks
        # (runs in a newly spawned thread)
        while not sig_stop.is_set():
            try:
                message = client.receive(block=True)
                self.show_log ('RECV: {} from {}'.format(message, client))
                # thread safe as .send is thread safe
                self.process_message(message)
            # if socket is closed during .receive
            except OSError:
                self.show_log ('socket closed')
                break
            #done

        self.show_log ('{} disconnected'.format(client.name))
        
        # kill the thread && cleanup. 
        # Otherwise, we will end up with a billion of references to null
        client.close()
        self.clients.pop(client, None)

        return

    def start_server (self):
        self.show_log("starting the server ...")

        with mido.sockets.PortServer('', self.tcp_port) as server:
            #threading.Thread(target=self.listen, daemon=True)

            self.show_log("server is listening on TCP/{}.".format(self.tcp_port))
            while True:
                try:
                    # Handle connections.
                    client = server.accept(block=True)
                    if client:
                        # creates a thread for each client
                        thread = self.accept_connection(client)
                        thread.start()

                except KeyboardInterrupt:
                    self.show_log("killing the server ...")
                    sig_stop.set()
                    break

                except Exception as E:
                    raise(E)

if __name__ == "__main__":
    Server = PlaybackServer()

