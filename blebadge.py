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
parser.add_argument("--blink", action="store_true",
	help="Enable message blinking")
parser.add_argument("--marquee", action="store_true",
	help="Enable moving circle around text")
#parser.add_argument("--timestamp", action="store_true",
#	help="Enable sending a current timestamp to the badge.")
parser.add_argument("--mac", required=True,
	help="The MAC address of the badge")
parser.add_argument("--text",
	help="The text to send to the badge")
parser.add_argument("--file", type=open,
	help="Input file to read texts from. " +
		"Format is <speed 1-8>,<mode>,<blink 0|1>,<marquee 0|1>,<text ...>. " +
		"One message per line, up to 8 messages are supported")

args = parser.parse_args()

messages = []
if args.text:
	messages.append((args.speed, args.mode, args.blink, args.marquee, args.text))
elif args.file:
	for line in args.file:
		if line[-1] == "\n":
			line = line[0:-1]

		split = line.split(",")
		if len(split) < 5:
			print("Invalid line in input file")
			exit(1)

		speed = int(split[0])
		mode = split[1]
		blink = int(split[2]) == 1
		marquee = int(split[3]) == 1
		text = ",".join(split[4:])

		if speed < 1 or speed > 8:
			print("Invalid speed " + split[0])
			exit(1)
		if mode not in modes:
			print("Invalid mode " + mode)
			exit(1)

		messages.append((speed, mode, blink, marquee, text))
else:
	print("Either --text or --file must be given")
	exit(1)

# TODO support sending an actual timestamp
timestamp = [0 for x in range(0, 16)]
spacer = [0 for x in range(0, 16)]

start = [
	0x77, 0x61, 0x6e, 0x67, 0x00, 0x00, #message header
	0, # blink flag, one bit per message
	0, # marquee, one bit per message
]
sizes = []
values = []

for i in range(0, 8):
	if i >= len(messages):
		start.append(0)
		sizes.append(0)
		sizes.append(0)
		continue
	
	speed, mode, blink, marquee, text = messages[i]
	options = ((speed - 1) << 4) | modes.index(mode)
	textLen = len(text)

	if blink:
		start[6] = start[6] | (1 << i)
	if marquee:
		start[7] = start[7] | (1 << i)

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
