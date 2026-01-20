import sys
from PIL import Image 
import os
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



def xor_encrypt(message_bytes , key): # Uses repeating key XOR
    key_bytes = key.encode("ascii")
    encrypted = bytearray()

    for i in range(len(message_bytes)):
        encrypted.append(message_bytes[i] ^ key_bytes[i % len(key_bytes)])

    return encrypted

def build_bitstream(message , key , mode):
    #convert message into bytes 
    message_bytes = message.encode("ascii")

    #Encyrpt the payload now
    encrypted_bytes = xor_encrypt(message_bytes , key)

    # Header = Message Length if 2 characters L = 2 smh
    L = len(encrypted_bytes)
    # header_bits = format(L , '032b') # 32 bit header
    mode_bit = "0" if mode == 1 else "1"
    header_bits = mode_bit + format(L , '032b')

    #Payload bits
    payload_bits = ""
    for byte in encrypted_bytes: 
        payload_bits += format(byte , '08b')
    
    #bitstream = header + payload
    return header_bits + payload_bits

def embed_bits(image_path , bitstream , mode , output_path):
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width , height = img.size

    bit_index = 0
    total_bits = len(bitstream)
    for y in range(height):
        for x in range(width):
            if bit_index >= total_bits:
                break 
            r , g , b = pixels[x,y]

            if mode == 1: # 1 channel steganography taking only red for 1 option 
                bit = int(bitstream[bit_index])
                if r % 2 != bit:
                    r -= 1 if r > 0 else r + 1
                pixels[x,y] = (r, g, b)
                bit_index += 1
            elif mode == 3: # 3 channel steganography for r , g and b 

                channels = [r, g, b]

                for i in range(3):
                    if bit_index >= total_bits:
                        break
                    bit = int(bitstream[bit_index])

                    if channels[i] % 2 != bit: 
                        channels[i] -= 1 if channels[i] > 0 else channels[i] + 1
                    bit_index += 1

                r, g, b = channels

            pixels[x,y] = (r, g, b)

        if bit_index >= total_bits:
                break
        
    img.save(output_path , format = "PNG") # for lossless 


def main():
    print("=================Steganography Encoder ==================")

    raw_input = input("Enter image file path: ")
    image_path = resolve_image_path(raw_input)

    if image_path is None:
        print("Error: Image file not found.")
        return
    message = input("Enter message to hide: ")
    key = input("Enter encryption key: ")
    mode = int(input("Enter mode (1 for 1-channel , 3 for 3-channel): "))

    output_path = input("Enter output filename: ")
    output_path += ".png"


    bitstream = build_bitstream(message , key , mode)
    embed_bits(image_path , bitstream , mode , output_path)

    print(f"Message Encoded Successfully in {output_path}")
    



if __name__ == "__main__":
    main()
