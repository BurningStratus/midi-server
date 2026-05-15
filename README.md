*** midi-server ***
- dependencies:
* mido
* python-rtmidi
* base python things such as venv/pip.

- set up venv:
```
0$ python -m venv venv
0$ cd venv && bin/pip install mido python-rtmidi && mkdir src && cd src
0$ git clone https://github.com/BurningStratus/midi-server.git
```

- usage:
Start the ./mido-server.py on the 'target' machine, and dont forget to set the sink to default sink:
```
0$ aconnect -l
client 0: 'System' [type=kernel]
    0 'Timer           '
	Connecting To: 142:0
    1 'Announce        '
	Connecting To: 142:0
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
client 142: 'PipeWire-System' [type=user,pid=4004]
    0 'input           '
	Connected From: 0:1, 0:0
client 143: 'PipeWire-RT-Event' [type=user,pid=4004]
    0 'input           '
```
In my case - 'Midi Through Port-0'. The server does a good job finding the default one itself.
Then, start the server:
```
0$ ./mido-server
++++ all ports: ['Midi Through:Midi Through Port-0 14:0']
++++ using port {} ... Midi Through:Midi Through Port-0 14:0
++++ Midi Through:Midi Through Port-0 14:0 opened.
++++ starting the server ...
++++ server is listening on 0.0.0.0 TCP/8100.
```

To kill the server, just press CTRL+C (SIGINT), and it will be killed 'gracefully'.

- on a client:
```
0$ ./mido-client.py # dont forget to swap the ip for the correct one
length note velocity:
midi> 1 60 100
```

On an example client, you will be greeted with a '''shell''', 
where you can send notes to server for testing purposes.
I'd suggest you try running the example input to 'hear' everything works.


