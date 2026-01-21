import sys 
import os
from PIL import Image

def resolve_image_path(filename):
    if os.path.exists(filename):
        return filename
    name , ext = os.path.splitext(filename)

    extensions = ['.png' , '.jpg' , '.jpeg' , '.bmp' , '.tiff']
    for e in extensions:
        canditate = name + e 
        if os.path.exists(canditate):
            return canditate
    return None


def xor_decrypt(cipher_bytes , key):
    key_bytes = key.encode("ascii")
    decrypted = bytearray()

    for i in range(len(cipher_bytes)):
        decrypted.append(cipher_bytes[i] ^ key_bytes[i % len(key_bytes)])

    return decrypted


def extract_bits(image_path , mode):
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width , height = img.size
    
    bits = ""

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x,y]

            if mode == 1:
                bits += str(r % 2)
            elif mode == 3:
                bits += str(r % 2)
                bits += str(g % 2)
                bits += str(b % 2)
    return bits 


def decode_message(bits , key):
    # Read header 
    mode_bit = bits[0]
    L = int(bits[1:33] , 2)
    actual_mode = 1 if mode_bit == "0" else 3

    #Read encrypted payload  only encrypted the message party of bit stream
    payload_bits = bits[33: 33 + (L * 8 )]
    encrypted_bytes = bytearray()

    for i in range(0 , len(payload_bits) , 8):
        encrypted_bytes.append(int(payload_bits[i:i+8] , 2))
    
    #Decrypt
    message_bytes = xor_decrypt(encrypted_bytes , key)
    return message_bytes.decode("ascii"), actual_mode

def main():
    print("=================Steganography Decoder ==================")

    raw_input = input("Enter image file path: ")
    image_path = resolve_image_path(raw_input)

    if image_path is None:
        print("Error: Image file not found.")
        return
    
    key = input("Enter decryption key: ")
    mode = int(input("Enter mode (1 for 1-channel , 3 for 3-channel): "))

    bits = extract_bits(image_path , 3) # mode replaced with 3 
    message , actual_mode = decode_message(bits , key) # Decode message and get actual mode used

    if mode != actual_mode:
        print("Error: Incorrect mode selected.")
        print("This was encoded in mode " , actual_mode)
        return


    print("Hidden Message: " , message)

if __name__ == "__main__":
    main()
