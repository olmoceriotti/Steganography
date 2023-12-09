import cv2
import argparse
import os

parser = argparse.ArgumentParser(description='A utility for image steganography.')
parser.add_argument('image_path', type=str, help='The source image path')
parser.add_argument('mode', choices=['enc', 'dec'], help="the desired mode")
parser.add_argument('-m', type =str, help='The message to embed')
parser.add_argument('-textIn', type =str, help='The message to embed')
parser.add_argument('--imgOut', type=str, help='Destination image path, if null the image will be overwritten')
parser.add_argument('--textOut', help="path for textfile, if not present it will be printed")

args = parser.parse_args()

print(args)

def path_check(path, png = False):
    if os.path.exists(path):
        if os.path.isfile(path):
            if png:
                if path.endswith(".png"):
                    return True
                else:
                    return False
            return True
    return False

def text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def embedMessageInImage(image, message):
    index = 0
    message += "".zfill(8)
    if(len(message) > height*width*channels):
        print("Impossible to embed the message")
    for x in range(width):
        for y in range(height):
            pixel = image[y, x]
            for channel in range(channels):
                if(index < len(message)):
                    pixel[channel] = pixel[channel] & ~1 | int(message[index])
                    index += 1
    return image

def extract_message(image):
    message = ""
    char = ""
    message_retrieved = False
    for x in range(width):
        if(message_retrieved): 
            break
        for y in range(height):
            pixel = image[y, x]
            for channel in range(channels):
                LSB = bin(pixel[channel])[2:].zfill(8)[7]
                char += LSB
                if len(char) % 8 == 0:
                    newChar = chr(int(char, 2))
                    char = ""
                    if(newChar == '\0'):
                        print("message retrieved")
                        return message
                    else:
                        message += newChar

if(path_check(args.image_path, True)):
    image = cv2.imread(args.image_path)
    cv2.imshow('image',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    height, width, channels = image.shape
else:
    raise ValueError("Invalid image path: " + args.image_path)

if(args.m != None):
    message = args.m
else:
    if(args.textIn != None and path_check(args.textIn)):
        file_path = args.textIn
        with open(file_path, 'r') as file:
            message = file.read()
    elif (args.mode == 'enc'):
        raise ValueError("No valid message provided " + args.image_path)

if(args.mode == 'enc'):
    binMessage = text_to_binary(message)
    resultImage = embedMessageInImage(image, binMessage)
    if(args.imgOut ==  None or (not path_check(args.imgOut, True))):
        cv2.imwrite(args.image_path, image)
    else:
        cv2.imwrite(args.imgOut, image)
    print("Converted")
else:
    extracted_message = extract_message(image)
    if(args.textOut != None and path_check(args.textOut)):
        with open(args.textOut, "w") as file:
            file.write(extracted_message)
    else:
        print(extracted_message)


"""
usage: steganography_tool.py [-h] [-m {lsb,dcs}] [-d DATA] [-o OUTPUT] {encode,decode} image

Steganography tool for PNG images.

positional arguments:
  {encode,decode}       Action to perform: encode or decode
  image                 Path to the input PNG image file

optional arguments:
  -h, --help            show this help message and exit
  -m {lsb,dcs}, --method {lsb,dcs}
                        Steganography method to use (default: lsb)
  -d DATA, --data DATA  Path to the file containing data to be encoded (required for encode)
  -o OUTPUT, --output OUTPUT
                        Path to the output PNG image file after encoding (required for encode)
  -i MESSAGE, --message MESSAGE
                        Message to be encoded directly from the command line (required for encode if data file is not provided)

    if args.action == 'encode':
        if not args.data and not args.message:
            parser.error("For encoding, either data file (-d) or message input (-i) is required.")
        if args.data and args.message:
            parser.error("Specify either data file (-d) or message input (-i), not both.")
        if args.data:
            encode(args.image, args.data, args.output, args.method)
            print("Encoding complete. Output saved to", args.output)
        else:
            encode(args.image, args.message, args.output, args.method)
            print("Encoding complete. Output saved to", args.output)
    elif args.action == 'decode':
        decode(args.image, args.method)
        print("Decoding complete.")
"""