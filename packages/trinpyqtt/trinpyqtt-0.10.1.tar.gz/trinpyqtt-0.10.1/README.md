# README #

trinpyqtt is a wrapper around the Paho MQTT python client, and simply extends
it with some convenience functions to facilitate building Smart-MQTT compliant
topics and data structures.
It furthermore contains some crypto tools to manage the username and
passwords as required by the Smart-MQTT brokers.


### What is this repository for? ###

* Use it when you need to connect to a Smart-MQTT broker from a python application
* [Trinity Smart](www.trintel.co.za)

With this client installed, you will be able to:

* Send commands directly to an identifiable RaspberryPi regardless of the connectivity layer. These commands can be sent via the Smart Web UI, or alternatively, via a REST API we can make available to you.
* Write your own code to act on custom built commands particular to your requirements
* If so configured, the client can also regularly posts health data to Smart - data about the underlying hardware. This includes stuff like the CPU temperature, the available disk space, and the top 5 processes currently running on the PI, and memory consumption.
* You can write your own client side checks to monitor the equipment you have connected to the Pi, and make that report to Smart as well
* You can send Smart events when something noteworthy happens at your application layer. These unsolicited events are logged by Smart, but:
* Smart also provides the tools - on the platform side - to build workflow pipelines for events. This can be things like writing the event to one of your Google spreadsheets, sending a Telegram, Pushbullet, Hipchat, or Pushover message to your phone. Or sending an SMS. In fact, our pipeline system is *very* flexible, and we would be able to on-route formatted versions of the events to just about anywhere (with a published API) 

### How do I get set up? ###
To install:
```bash
pip3 install --upgrade trinpyqtt
```
In order for your Raspberry Pi to be able to join the Smart MQTT broker, it need
to pe able to generate a compliant password. This library provides some utility functions
to help you do that:

#### Password ####
In order to connect to the Smart-MQTT brokers, your MQTT client needs to present
a unique username and password.

After you installed the library, but before you can run the sample code, you 
would need to create a password directly on the RaspPi: This needs to be run as 
root, as it needs to write into the /opt directory directly.

__NOTE:__ You need an account on SMART, and your user needs to have "Auto Provision" 
privileges enabled in order for you to perform the next steps.

```bash
sudo python3
```
Then from inside the interpreter
```
Python 3.5.3 (default, Jan 19 2017, 14:11:04) 
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from trinpyqtt.tools.cryptools import auto_register
>>> from trinpyqtt.models import raspberrypi as model
>>> USERNAME = 'your_username_on_smart'
>>> PASSWORD = 'your_login_password_on_smart'
>>> auto_register(USERNAME, PASSWORD, model)
```
it should reply with:
```
    Done. 
    Your PROFILE_ID is: NNNNNNNN 
    Your UID(Device Unique ID) is: XXXXXXXXXXXXXXX 
    This should be added to SMART.
```

Once done, you should (for security purposes) zap your local Python history file. From your terminal just issue:

```bash
> .python_history
```

The above steps will:

* create a password unique to that particular Pi on the /opt/trinity directory (which is why you need root).
That password is read and hashed by the trinpyqtt client every time it connects
to the broker. You should not need to worry about it further. It also will only
work from the hardware on which it was generated. It is not portable.
* create a world readable file with your PROFILE_ID in it. In the past this needed to be passed
into the constructor of the client, but is now read directly from the file system.

#### Identity ####
The client reads some hardware information, to identify itself.
This identity should be seeded on Smart in order to start using Smart.
On a RaspberryPI the identity is derived from the hardware serial number, and
on an Linux box it is derived from the MAC addresses of the NICs.

##### UID #####
To read the identity of the unit:
```bash
python3
```
```python
from trinpyqtt.models.raspberrypi import get_uid
get_uid() # 'XXXXXXXXXXXXXXX'
```
This ID is used by Smart to uniquely identify this hardware, and is called 
the 'Device Unique ID' on that platform.

##### PROFILE_ID #####
To read your PROFILE_ID:
```bash
python3
```
```python
from trinpyqtt.tools.cryptools import read_cid
read_cid() # 'NNNNNNNN'
```
This ID is part of the comms security, and is used to identify all the units on the system
that belong to you. It is sometimes also called a "CID" or "Customer ID."
It has no direct user-application usefulness, and is mentioned here for interest only.

# Sample Application #
See the "demo" directory for a sample application suitable for a RaspberryPi.
This is a sample application showing the use of the client, along with your
own logic. Take note:

* The *APP_ID* constant can be chosen to be any string, but ultimatly needs to tie up with an ASSET_ID on Smart
* When running this application for the first time an __ini__ file will be created in the user's home directory. This file will contain the settings passed in during the constructor (when run the first time). When the application is stopped and restarted, the ini file is read, and takes precedence over the constructor argumants. This is to ensure that any user settings passed to the appplication via a command from Smart is persisted accross reboots.

### Note ###
Once the ini file is created, you need to clear it by hand if you want to start fresh. For instance, if you 
change the broker host in your code, then you need to clear the ini file, as the host setting is persisted there, 
and takes precedence over the arguments passed to the TrinClient constructor.

### Note ###
The sample application shows the use of SSL comms, and assumes the server public 
key file is installed at the shown location.
This public key file is available on request from Trinity.

To test this setup, assume that this client is connected to a MQTT server on
your local box, then issue this command to produce a "c" message that will
be processed by the example script above:
```bash
mosquitto_pub -d -h localhost -p 1883 -t 'NNNNNNNN/XXXXXXXXXXXXXXX/my_app_id/</' -m '{"c": [123456789,">a_tct", ["sum_these",1,2,3]]}' -q 1
```

# Run as a service #
These are guidelines that worked for us, but you may have wildly differing views
on how to achieve the same. We chose to run this as a _systemd_ service, and these
guidelines may be followed to do the same. However your mileage may vary.

With the setup below, our application is started on system boot, and is run
with the pi user privileges. We furthermore log client messages to 
'/var/log/trinmqtt/trinmqtt.log'

Create a systemd startup service file called "trinmqtt.service"
```bash
sudo vi /etc/systemd/system/trinmqtt.service
```
and add this to the file
```bash
[Unit]
Description=Trinity Smart MQTT Client

[Service]
WorkingDirectory=/home/pi/Workspace
ExecStart=/usr/bin/python3 /home/pi/Workspace/mqtt.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=trinmqtt
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

Once done and saved enable it by issuing:
```bash
sudo systemctl enable trinmqtt
```

You should now be able to start the service with:
```bash
sudo systemctl start trinmqtt
```

or see its status with:
```bash
sudo systemctl status trinmqtt
```

or to see its logs:
```bash
journalctl -u trinmqtt
```

#### Logging (When run as a service) ####
To make this log out to somewhere else (in addition to the systemd journal):
Choose and create where you would want to log to:
```bash
sudo mkdir /var/log/trinmqtt
sudo touch /var/log/trinmqtt/trinmqtt.log
sudo chown -R pi:pi /var/log/trinmqtt
```
then add a file to the rsyslog.d directory
```bash
sudo vi /etc/rsyslog.d/trinmqtt.conf
```
then in that file tie the name of your service to the required log file
```
if $programname == 'trinmqtt' then /var/log/trinmqtt/trinmqtt.log
if $programname == 'trinmqtt' then stop
```

then restart both the rsyslog service and the trinmqtt service
```bash
sudo systemctl restart rsyslog
sudo systemctl restart trinmqtt
```

You can check that the log file is being written here...
```bash
tail -100f /var/log/trinmqtt/trinmqtt.log 
```

To check the ini file is in the user's directory
```bash
cat ~/.config/trinmqtt/trinmqtt.ini
```


### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* jan@trintel.co.za
