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
                   [--flash] [--marquee] --mac MAC
                   text

Set content of BLE LED Name Badge

positional arguments:
  text                  The text to send to the badge

required arguments:
  --mac MAC             The MAC address of the badge

optional arguments:
  -h, --help            show this help message and exit
  --speed {1,2,3,4,5,6,7,8}
                        Set animation speed
  --mode {left,right,up,down,fixed,cycle,falldown,television,laser}
                        Set animation mode
  --flash               Enable message flashing
  --marquee             Enable moving circle around text
```