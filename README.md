# BLE Name Badge

Python script to set contents of Bluetooth low energy enabled LED name badges.
You can buy them e.g. on [Aliexpress](https://fr.aliexpress.com/item/Sign-Scrolling-advertising-business-card-show-digital-display-tag-LED-name-badge-Rechargeable-Programmable-White/32759781214.html), I bought mine on [35c5](https://en.wikipedia.org/wiki/Chaos_Communication_Congress) from @fossasia. There is an official app from the seller and a [FOSS android app written in Kotlin](https://github.com/Nilhcem/ble-led-name-badge-android) by @Nilhcem. 

As I didnt want to run the "official" app and as I do not use an Android phone i wrote this python script. @Nilhcem's app as well as his [blog post](http://nilhcem.com/iot/reverse-engineering-bluetooth-led-name-badge) were very helpful!

## Installing
```
# apt install gattool
$ git clone https://github.com/M4GNV5/BluetoothLEDBadge
```

## Usage
```
usage: blebadge.py [-h] [--speed {1,2,3,4,5,6,7,8}]
                   [--mode {left,right,up,down,fixed,cycle,falldown,television,laser}]
                   [--blink] [--marquee] --mac MAC [--text TEXT] [--file FILE]

Set content of BLE LED Name Badge

optional arguments:
  -h, --help            show this help message and exit
  --speed {1,2,3,4,5,6,7,8}
                        Set animation speed
  --mode {left,right,up,down,fixed,cycle,falldown,television,laser}
                        Set animation mode
  --blink               Enable message blinking
  --marquee             Enable moving circle around text
  --mac MAC             The MAC address of the badge
  --text TEXT           The text to send to the badge
  --file FILE           Input file to read texts from. Format is <speed
                        1-8>,<mode>,<blink 0|1>,<marquee 0|1>,<text ...>. One
                        message per line, up to 8 messages are supported
```