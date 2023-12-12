"""
Steps:
1) Calulate difference between non overlapping pairs of pixels in a zig zag manner [X]
2) Calculate nearest perfect square [X]. Search for the correct range [X]. Determine how many bits [X]
3) Read m bits from the message stream and convert them in the decimal number b [X]
4) Calculate d' [X] and check it's in the same range as d [X]
5)  Calculate new pixel values [x]

print(str(i) + ": " + "{0:b}".format(i) + " && " + "{0:b}".format(int(2**(m + 1) -1)) + " && " + b + "===" + str(i & int(2**(m))))
print(str(i) + ": " + "{0:b}".format(i) + " && " + "{0:b}".format(int(2**(m) -1)) + " && " + b + "===" + "{0:b}".format(i & int(2**(m) -1)))
"""

import cv2
import numpy as np

def nearest_perfect_square_scalar(num):
    num += 1 #To adhere to quantization table defined in the paper
    nearest_perfect_square = int(np.sqrt(num)) ** 2
    next_perfect_square = (int(np.sqrt(num)) + 1) ** 2
    if np.abs(num - nearest_perfect_square) <= np.abs(num - next_perfect_square):
        return int(np.sqrt(nearest_perfect_square))
    else:
        return int(np.sqrt(next_perfect_square))
    
nearest_perfect_square = np.vectorize(nearest_perfect_square_scalar)

def embed_values(distance, binary):
    m_container = np.full(len(distance), -1, dtype=int)
    d1_container = np.full(len(distance), -1, dtype=int)
    for i in range(0, len(distance)):
        next = False
        if binary == "Finished":
            break
        n = nearest_perfect_square_scalar(distance[i])
        if n < 16:
            m = int(np.floor(np.log2(n * 2)))
            l = n * (n-1)
            u = (n**2 +n) - 2**m
            if distance[i] < u:
                b, binary_temp = extract_bits_scalar(binary, m + 1)
                b = "{0:b}".format(b).zfill(m + 1)
                
                for j in range(l, u):
                    #print(str(j) + ": " + "{0:b}".format(j) + " & mask: " + "{0:b}".format(int(2**(m + 1) -1)) + " && " + b + " bitwise &:" + "{0:b}".format(j & int(2**(m + 1) - 1)))
                    if ("{0:b}".format(j & int((2**(m + 1)) - 1)).zfill(m) == b):
                        binary = binary_temp
                        m_container[i] = int(m+1) 
                        d1_container[i] = j
                        next = True
                        break
            if not next:
                b, binary_temp = extract_bits_scalar(binary, m)
                b = "{0:b}".format(b).zfill(m)
                
                for j in range(u, n*(n+1)): #Manca -1?
                    #print(str(j) + ": " + "{0:b}".format(j) + " & mask: " + "{0:b}".format(int(2**(m) -1)) + " && " + b +  " bitwise &: " + "{0:b}".format(j & int(2**(m) - 1)))
                    if ("{0:b}".format(j & int((2**m)-1)).zfill(m) == b):
                            binary = binary_temp
                            m_container[i] = int(m) 
                            d1_container[i] = j
                            next = True
                            break
            if not next:            
                m_container[i] = -1000
                d1_container[i] = -1000
        else:
            b, binary = extract_bits_scalar(binary, 4)
            m_container[i] = 4 
            d1_container[i] = 240 + b
    return m_container, d1_container, binary

def text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def extract_bits_scalar(bin, m):
    b = ""
    if(len(bin) > (m)):
        b = int(bin[:m], 2)
        bin = bin[m:]
    else:
        b = int(bin.zfill(m), 2)
        bin = "Finished"
    return b, bin

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

def embed_in_pixels(pixel1 , pixel2, binary):
    d = np.abs(pixel2.astype(int)-pixel1.astype(int))
    _, d1, binary = embed_values(d, binary)
    pixel1, pixel2 = new_pixels(pixel1, pixel2, d, d1)
    return pixel1, pixel2, binary

def new_pixels_single_channel(pixel1, pixel2, d, d1):
    if pixel1 >= pixel2 and d1 > d:
        if(d1 != -1):
            pixel1 = pixel1 + np.ceil(np.abs(d1-d)/2)
            pixel2 = pixel2 - np.floor(np.abs(d1-d)/2)
    if pixel1 < pixel2 and d1 > d:
        if(d1 != -1):
            pixel1 = pixel1 - np.ceil(np.abs(d1-d)/2)
            pixel2 = pixel2 + np.floor(np.abs(d1-d)/2)
    if pixel1 >= pixel2 and d1 <= d:
        if(d1 != -1):
            pixel1 = pixel1 - np.ceil(np.abs(d1-d)/2)
            pixel2 = pixel2 + np.floor(np.abs(d1-d)/2)
    if pixel1 < pixel2 and d1 <= d:
        if(d1 != -1):
            pixel1 = pixel1 + np.ceil(np.abs(d1-d)/2)
            pixel2 = pixel2 - np.floor(np.abs(d1-d)/2)
    return int(pixel1), int(pixel2)

new_pixels = np.vectorize(new_pixels_single_channel)

def extraction(image):
    height, width, _ = image.shape
    i = 0
    offset = 0
    acc = ""
    acc2 = "" 
    result = ""
    finished = False
    for x in range(0, height):
        if x % 2 == 0:
            for y in range(0 + offset, width, 2):
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
        
                #acc_array = extract_from_pixels(pixel1, pixel2)
                for i in range(0, len(pixel1)):
                    sub = extract_from_pixels_scalar(pixel1[i], pixel2[i])
                    acc = acc + sub
                    acc2 = acc2 + sub
                while len(acc) >= 8:
                    int_char = int(acc[:8], 2)
                    acc = acc[8:]
                    result = result + chr(int_char)
                    if int_char == 0:
                        finished = True
                        break
                if finished:
                    break            
            if finished:
                break
        else:
            for y in range(width -1 - offset, -1, -2):
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
                    break
                
                for i in range(0, len(pixel1)):
                    sub = extract_from_pixels_scalar(pixel1[i], pixel2[i])
                    acc = acc + sub
                    acc2 = acc2 + sub
                while len(acc) >= 8:
                    int_char = int(acc[:8], 2)
                    acc = acc[8:]
                    result = result + chr(int_char)
                    if int_char == 0:
                        finished = True
                        break
                if finished:
                    break            
            if finished:
                break
        if finished:
            break
    if finished:
        print("Message retrieved successfully")
    return result[:len(result) - 1]

def extract_from_pixels_scalar(pixel1, pixel2):
    d1 = np.abs(int(pixel2)-int(pixel1))
    n = nearest_perfect_square_scalar(d1)
    acc = ""
    if(d1 >= 240):
        acc = acc + bin(d1 & ((1 << 4) - 1))[2:].zfill(4)
    else:
        m = int(np.floor(np.log2(2 * n)))
        if ((n**2+n) - (n**2 -n)) > 2**m and d1 < ((n**2)+n) - (2**m):
            acc = acc + bin(d1 & ((1 << (m+1)) - 1))[2:].zfill(m+1)
        else:
            acc = acc + bin(d1 & ((1 << m) - 1))[2:].zfill(m)
    return acc

extract_from_pixels = np.vectorize(extract_from_pixels_scalar)


image = cv2.imread("./file9.png")
height, width, channels = image.shape

message = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
print(f"Message: {message}")
message = message + '\0'
binary = text_to_binary(message)
print(f"Message bin: {binary}")
i = 0
offset = 0
m = []

for x in range(0, height):
    if(binary == "Finished"):
                break
    if x % 2 == 0:
        for y in range(0 + offset, width, 2):
            if(binary == "Finished"):
                break
            offset = 0
            pixel1 = image[x, y]
            print(pixel1)
            i += 1
            if y + 1 < width:
                pixel2 = image[x, y + 1]
                i += 1
            elif x + 1 < height:
                pixel2 = image[x + 1, y]
                offset = 1
                i += 1
            else:
                print("Error: Reached end")
                break

            pixel1, pixel2, binary = embed_in_pixels(pixel1, pixel2, binary)  
            print(pixel1)         
            image[x, y] = pixel1
            if y + 1 < width:
                image[x, y + 1] = pixel2
            elif x + 1 < height:
                image[x + 1, y] = pixel2
    else:
        for y in range(width -1 - offset, -1, -2):
            if(binary == "Finished"):
                break
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
                print("Error: Reached end")
                break
            
            pixel1, pixel2, binary = embed_in_pixels(pixel1, pixel2, binary)
            
            image[x, y] = pixel1
            if y - 1 >= 0:
                image[x, y - 1] = pixel2
            elif x + 1 < height:
                image[x + 1, y] = pixel2



cv2.imshow('Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("file10.png", image)

image2 = cv2.imread("./file10.png")
print(f"Extracted the string: {extraction(image2)}")
