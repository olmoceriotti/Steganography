from PIL import Image

# Function to hide a text message in an image using LSB steganography
def hide_text_in_image(input_image_path, output_image_path, message):
    try:
        # Open the image
        image = Image.open(input_image_path)

        # Convert the message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)

        if len(binary_message) > (image.width * image.height * 3):
            raise ValueError("Message is too large to hide in the image")

        data_index = 0

        # Iterate through the image pixels
        for x in range(image.width):
            for y in range(image.height):
                pixel = list(image.getpixel((x, y)))

                # Iterate through the RGB channels (3 channels per pixel)
                for color_channel in range(3):
                    if data_index < len(binary_message):
                        pixel[color_channel] = pixel[color_channel] & ~1 | int(binary_message[data_index])
                        data_index += 1

                image.putpixel((x, y), tuple(pixel))

        # Save the modified image with the hidden message
        image.save(output_image_path)
        print("Message hidden successfully.")
    
    except Exception as e:
        print(f"Error: {e}")

# Function to extract the hidden text from an image
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)

        binary_message = ""
        data_index = 0

        for x in range(image.width):
            for y in range(image.height):
                pixel = list(image.getpixel((x, y))

                for color_channel in range(3):
                    binary_message += str(pixel[color_channel] & 1)
                    data_index += 1

                    if data_index % 8 == 0:
                        char = chr(int(binary_message, 2))
                        if char == '\0':  # Null character marks the end of the message
                            print("Message extracted successfully.")
                            return
                        print(char, end="")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
input_image_path = 'input_image.png'
output_image_path = 'output_image.png'
message_to_hide = "Hello, this is a hidden message!"

# Hide the message in the image
hide_text_in_image(input_image_path, output_image_path, message_to_hide)

# Extract the hidden message from the image
extract_text_from_image(output_image_path)
