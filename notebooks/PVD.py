"""
[𝑛2 − 𝑛, 𝑛2 + 𝑛−2𝑚] and [𝑛2 +𝑛−2𝑚 +1,𝑛2 +𝑛−1].
Implementare questa definzione di subrange
Sistemare nearest perfect square
"""

import cv2
from math import floor, log2
import numpy as np

def nearest_perfect_square_scalar(d):
    for i in range(1, 16):
        if d >= i**2 and d < (i+1)**2:
            return i if abs(d - i**2) < abs(d - (i+1)**2) else (i+1)
    return 1
nearest_perfect_square = np.vectorize(nearest_perfect_square_scalar)

def secret_bits_number_scalar(n):
    if n > 0:
        return floor(log2(n * 2))
    else:
        return 1
secret_bits_number = np.vectorize(secret_bits_number_scalar)

def text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def extract_bits(bin, m):
    b = np.full(len(m), 0, dtype=int)
    for j in range(0, len(m)):
        if(bin == "Finished"):
            break
        if(len(bin) > (m[j])):
            b[j] = int(bin[:m[j]], 2)
            bin = bin[m[j]:]
        else:
            b[j] = int(bin.zfill(m[j]), 2)
            bin = "Finished"
    return b, bin

image = cv2.imread("./file1.png")
height, width, channels = image.shape

message = "messaggio"
bin = text_to_binary(message)
print(f"Message: {message}")
print(f"Message bin: {bin}")
i = 0
offset = 0
d = []
m = []

for x in range(0, height):
    if(bin == "Finished"):
                break
    if x % 2 == 0:
        for y in range(0 + offset, width, 2):
            print(f"X, Y: {x}, {y}")
            offset = 0
            pixel1 = image[x, y]
            i += 1
            if y + 1 < width:
                pixel2 = image[x, y + 1]
                i += 1
            elif x + 1 < height:
                pixel2 = image[x + 1, y]
                offset = 1
                i += 1
            else:
                print("Reached end")
                break

            distance = np.abs(pixel2.astype(int)-pixel1.astype(int))
            print(f"Distance: {distance}")
            d.append(distance)
            n = nearest_perfect_square(distance)
            print(f"N: {n}")
            m = secret_bits_number(n)
            print(f"M: {m}")
            print(f"Bin: {bin}")
            b, bin = extract_bits(bin, m)
            print(f"b: {b}")
            print(f"Bin: {bin}")
            if(bin == "Finished"):
                break
            l1 = np.where(n > 1, n * (n - 1), 1)
            d1 = l1 + b
            print(f"l1: {l1}")
            print(f"d1: {d1}")
            print(f"Perfectsquare: {nearest_perfect_square(d1)}")
            print(n==nearest_perfect_square(d1))
    else:
        for y in range(width -1 - offset, -1, -2):
            print(f"X, Y: {x}, {y}")
            offset = 0
            pixel1 = image[x, y]
            i += 1
            if y - 1 >= 0:
                pixel2 = image[x, y - 1]
                i += 1
            elif x + 1 < height:
                pixel2 = image[x + 1, y]
                offset = 1
                i += 1
            else:
                print("Reached end")
                break

            distance = np.abs(pixel2.astype(int)-pixel1.astype(int))
            print(f"Distance: {distance}")
            d.append(distance)
            n = nearest_perfect_square(distance)
            print(f"N: {n}")
            m = secret_bits_number(n)
            print(f"M: {m}")
            print(f"Bin: {bin}")
            b, bin = extract_bits(bin, m)
            print(f"b: {b}")
            print(f"Bin: {bin}")
            if(bin == "Finished"):
                break
            l1 = n-1 * n
            d1 = l1 + b
            print(f"l1: {l1}")
            print(f"d1: {d1}")
            print(n==nearest_perfect_square(d1))