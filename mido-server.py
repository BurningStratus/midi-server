#!/usr/bin/env -S ../bin/python

import mido
import threading
from time import sleep

class PlaybackServer:
    def __init__ (self, tcp_port=8100):
        self.tcp_port =     tcp_port
        self.clients =      []
        self.port =         self.init_output_port()
        self.exit_code =    self.start_server()

    def show_log (self, *args):
        print ("++++", *args)

    def init_output_port (self):
        ports = mido.get_output_names()

        self.show_log ("all ports:", ports)
        self.show_log ("using port {} ...", ports[0])

        mido.open_output(ports[0])

        self.show_log ("{} opened.".format(ports[0]))

        return ports[0]

    def accept_connection (self, client):
        self.show_log ('Connection from {}'.format(client.name))

        # spawn a thread to listen to events there
        thread = threading.Thread(target=self.client_instance, daemon=True, args=(client,))

        self.clients.append( (thread, client) )
        self.show_log ('spawn thread for: {}'.format(client.name))

        # OLD # client in enumerate(self.clients):
        #                     (thread, client)
        # for index in range(len(self.clients)):
        #     client = self.clients[index] 
        #     if client[1].closed:
        #         self.show_log ('{} disconnected'.format(client[1].name))
        #         #self.clients[index][0].join()
        #         # close the thread
        #         #client[0].join()
        #         self.show_log ('killing the thread {} ...'.format(client[0]))
        #         del self.clients[index]

        return thread

    def message_callback(self, message):

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
        while True:
            for message in client.iter_pending():
                self.show_log ('Received {} from {}'.format(message, client))

                # thread safe as .send is thread safe
                self.message_callback(message)

            # thread is killed automatically here
            if client.closed:
                self.show_log ('{} disconnected'.format(client.name))
                
                # cleanup. 
                # Otherwise, we will end up with a billion of references to null
                for e in self.clients:
                    # fugly :/
                    if e[1] == client:
                        self.clients.remove(e)
                        break
                #done

                # try:
                # except ValueError:
                #     self.show_log ('failed to remove the reference: {}.'.format(client))
                #     pass

                #self.clients.pop(client) # int
                #del self.clients[client]

                return

            #done
        #done


    def start_server (self):
        self.show_log("starting the server ...")


        with mido.sockets.PortServer('', self.tcp_port) as server:
            #threading.Thread(target=self.listen, daemon=True)

            self.show_log("server is listening on 0.0.0.0 TCP/{}.".format(self.tcp_port))
            while True:
                try:
                    # Handle connections.
                    client = server.accept(block=False)
                    if client:
                        # creates a thread for each client
                        thread = self.accept_connection(client)
                        thread.start()

                except KeyboardInterrupt:
                    self.show_log("killing the server ...")

                    self.show_log("killing the threads ...")
                    for client in self.clients:
                        self.show_log("killing thread {} ... ".format(client[0].native_id)) 
                        client[0].join()
                    break

                except Exception as E:
                    raise(E)

if __name__ == "__main__":
    Server = PlaybackServer()

