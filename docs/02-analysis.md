# Analysis

## Problem Overview
This project focuses on securely embedding a secret message inside a digital image using binary-based techniques.

## Motivation
Traditional encryption makes data unreadable but visible. Steganography aims to hide the existence of the message itself.

## Approach Overview
The system uses binary manipulation of image pixel values to embed information while preserving visual quality.

## Character Encoding
The system represents secret messages using an 8-bit character encoding. Each character occupies exactly one byte (8 bits). For example, the character 'H' is represented as 01001000 in binary. Special characters such as spaces are treated as ordinary characters and are encoded using their ASCII values.

## Data Structure of the Hidden Message
The hidden data embedded in the image is structured as a continuous binary sequence consisting of two parts: a fixed-length header followed by a variable-length message payload.

### Header
The header occupies the first 32 bits of the embedded data. It stores an integer L, which represents the number of bytes in the secret message.

### Message Payload
Following the header, the message payload consists of exactly 8L bits. Each group of 8 bits represents one character of the message.

## Bit Indexing and Ordering
Let b₀, b₁, b₂, ... represent the extracted least significant bits of pixel values in traversal order. The header occupies bits b₀ to b₃₁. The message payload occupies bits b₃₂ to b₍₃₂₊₈L₋₁₎. The ordering of bits is determined implicitly by the fixed traversal order of image pixels.

## Termination of Decoding
During decoding, the first 32 bits are read to determine the value of L. The decoder then reads exactly 8L additional bits to reconstruct the message. Once these bits are processed, decoding terminates. Any remaining pixel data is ignored.
