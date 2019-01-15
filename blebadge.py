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
parser.add_argument("--image",
	help="Image file to display on the badge. (height needs to be 11)")
parser.add_argument("--video",
	help="Video file to display on the badge. (height needs to be 11, width should be 44)")

args = parser.parse_args()

messages = []

def textToData(text):
	text = text.decode("utf-8")
	data = []
	for c in text:
		data.extend(letters[c])

	return data

def imageToData(img):
	h, w = img.shape
	if h != 11:
		print("Invalid image height: " + str(h) + ". Needs to be 11")
		exit(1)

	byteW = w / 8
	if w % 8 != 0:
		byteW = byteW + 1

	data = []
	for row in range(0, byteW):
		for y in range(0, 11):
			byte = 0
			for col in range(0, 8):
				x = row * 8 + col
				if x >= w:
					continue

				if img[y][x] > 128:
					byte = byte | (1 << (7 - col))

			data.append(byte)

	return data

if args.text:
	data = textToData(args.text)
	messages.append((args.speed, args.mode, args.blink, args.marquee, data))
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

		data = textToData(text)
		messages.append((speed, mode, blink, marquee, data))
elif args.image:
	import cv2

	img = cv2.imread(args.image, 0)
	data = imageToData(img)

	messages.append((args.speed, args.mode, args.blink, args.marquee, data))
elif args.video:
	import cv2, numpy as np

	vid = cv2.VideoCapture(args.video)
	ret, long_img = vid.read()

	h, w, c = long_img.shape
	if w != 44 or h != 11:
		print("Invalid video format, needs to be 44x11, but is " + str(w) + "x" + str(h))
		exit(1)

	while vid.isOpened():
		ret, img = vid.read()
		if not ret:
			break
		long_img = np.concatenate((long_img, img), axis=1)

	long_img = cv2.cvtColor(long_img, cv2.COLOR_BGR2GRAY)
	data = imageToData(long_img)
	messages.append((8, "fixed", False, False, data))

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

	speed, mode, blink, marquee, data = messages[i]
	options = ((speed - 1) << 4) | modes.index(mode)
	textLen = len(data) / 11

	if blink:
		start[6] = start[6] | (1 << i)
	if marquee:
		start[7] = start[7] | (1 << i)

	start.append(options)

	sizes.append((textLen & 0xffff) >> 8)
	sizes.append(textLen & 0xff)

	values.extend(data)

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

print "Sending ", len(packages), " packages..."
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
