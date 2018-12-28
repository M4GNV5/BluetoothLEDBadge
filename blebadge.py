import argparse
import json
from subprocess import call

modes = ["left", "right", "up", "down", "fixed", "cycle", "falldown", "television", "laser"]

with open("./letters.json", "r") as fd:
	lettersHex = json.load(fd)
	letters = {}
	for letter in lettersHex:
		representation = []
		representationHex = lettersHex[letter]
		for i in range(0, len(representationHex) / 2):
			hex = representationHex[i * 2 : i * 2 + 2]
			representation.append(int(hex, 16))

		letters[letter] = representation

parser = argparse.ArgumentParser(description="Set content of BLE LED Name Badge")
parser.add_argument("--speed", type=int, default=4, choices=range(1, 9),
	help="Set animation speed")
parser.add_argument("--mode", default="left", choices=modes,
	help="Set animation mode")
parser.add_argument("--flash", action="store_true",
	help="Enable message flashing")
parser.add_argument("--marquee", action="store_true",
	help="Enable moving circle around text")
#parser.add_argument("--timestamp", action="store_true",
#	help="Enable sending a current timestamp to the badge.")
parser.add_argument("--mac", required=True,
	help="The MAC address of the badge")
parser.add_argument("text",
	help="The text to send to the badge")

args = parser.parse_args()

# TODO support multiple messages (up to 8 are supported by the module)
messages = [(args.speed, args.mode, args.text)]

# TODO support sending an actual timestamp
timestamp = [0 for x in range(0, 16)]
spacer = [0 for x in range(0, 16)]

start = [
	0x77, 0x61, 0x6e, 0x67, 0x00, 0x00, #message header
	1 if args.flash else 0,
	1 if args.marquee else 0
]
sizes = []
values = []

for i in range(0, 8):
	if i >= len(messages):
		start.append(0)
		sizes.append(0)
		sizes.append(0)
		continue
	
	speed, mode, text = messages[i]
	options = ((speed - 1) << 4) | modes.index(mode)
	textLen = len(text)
	
	start.append(options)

	sizes.append((textLen & 0xffff) >> 8)
	sizes.append(textLen & 0xff)

	for c in text:
		values.extend(letters[c])

while len(values) % 16 != 0:
	values.append(0)

packages = [
	start,
	sizes,
	timestamp,
	spacer,
]

while len(values) > 0:
	part = values[0 : 16]
	packages.append(part)
	del values[0 : 16]

for part in packages:
	hex = ''.join(format(x, '02x') for x in part)
	cmd = ["gatttool",
		"--device=" + args.mac,
		"--char-write-req",
		"--handle=0x1a",
		"--value=" + hex
	]

	print(" ".join(cmd))
	call(cmd)
