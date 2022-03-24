from __future__ import absolute_import, division, print_function, with_statement, unicode_literals

# import pyparsing
import generator
import tables
import io
import itertools
import math


class QRCodeBuilder:
    """This class generates a QR code based on the standard. It is meant to
    be used internally, not by users!!!
    """

    def __init__(self, data, version, mode, error):
        """See :py:class:`QR.init` for information on the parameters."""
        # Set what data we are going to use to generate
        # the QR code
        self.data = data
        # print("main data:"+self.data.__repr__())                                       #print added by udoy
        # Check that the user passed in a valid mode
        if mode in tables.modes:
            self.mode = tables.modes[mode]
        else:
            raise ValueError('{0} is not a valid mode.'.format(mode))

        # print("Mode specified by code:"+ str(self.mode))                          #print added by udoy

        # Check that the user passed in a valid error level
        if error in tables.error_level:
            self.error = tables.error_level[error]
        else:
            raise ValueError('{0} is not a valid error '
                             'level.'.format(error))

        if 1 <= version <= 40:
            self.version = version
        else:
            raise ValueError("Illegal version {0}, version must be between "
                             "1 and 40.".format(version))

        # print("version detected by code:"+str(version))                               #print added by udoy

        # Look up the proper row for error correction code words
        self.error_code_words = tables.eccwbi[version][self.error]

        # This property will hold the binary string as it is built
        self.buffer = io.StringIO()

        # Create the binary data block
        self.add_data()
        # self.
        # Create the actual QR code
        # comment make code to see what happend
        # self.make_QR_code(self)                                                #make code run part.
        # print(self.buffer.getvalue())
        # print(len(self.buffer.getvalue()))
        """data spliter"""
        splited_data = self.data_spliter(self.buffer.getvalue())

        # print(f"splitted_data: {splited_data}")
        # print(self.buffer.getvalue())
        # #below line code commented out because got update version.
        # self.generator = generator.generator(self.buffer.getvalue(),version, mode, error)
        self.generator = generator.generator(splited_data, version, mode, error)
        # print(f"generator create data:{self.generator.final_matrix}")
        self.final_gen_matrix = self.generator.final_matrix
        """this line is added to see the output value in terminal."""
        # print("final matrix is:")
        # for i in range(self.generator.final_matrix_size):
        #     print(self.final_gen_matrix[i])

    def grouper(self, n, iterable, fillvalue=None):
        """This generator yields a set of tuples, where the
        iterable is broken into n sized chunks. If the
        iterable is not evenly sized then fillvalue will
        be appended to the last tuple to make up the difference.

        This function is copied from the standard docs on
        itertools.
        """
        args = [iter(iterable)] * n
        if hasattr(itertools, 'zip_longest'):
            return itertools.zip_longest(*args, fillvalue=fillvalue)
        return itertools.zip_longest(*args, fillvalue=fillvalue)

    def binary_string(self, data, length):
        """This method returns a string of length n that is the binary
        representation of the given data. This function is used to
        basically create bit fields of a given size.
        """
        return '{{0:0{0}b}}'.format(length).format(int(data))

    def get_data_length(self):
        """QR codes contain a "data length" field. This method creates this
        field. A binary string representing the appropriate length is
        returned.
        """

        # The "data length" field varies by the type of code and its mode.
        # discover how long the "data length" field should be.
        if 1 <= self.version <= 9:
            max_version = 9
        elif 10 <= self.version <= 26:
            max_version = 26
        elif 27 <= self.version <= 40:
            max_version = 40

        data_length = tables.data_length_field[max_version][self.mode]

        if self.mode != tables.modes['kanji']:
            length_string = self.binary_string(len(self.data), data_length)
        else:
            length_string = self.binary_string(len(self.data) / 2, data_length)

        if len(length_string) > data_length:  # i need to see this part again to check or push twice data
            raise ValueError('The supplied data will not fit '
                             'within this version of a QRCode.')
        return length_string

    def encode(self):
        """This method encodes the data into a binary string using
        the appropriate algorithm specified by the mode.
        """
        if self.mode == tables.modes['alphanumeric']:
            encoded = self.encode_alphanumeric()
        elif self.mode == tables.modes['numeric']:
            encoded = self.encode_numeric()
        elif self.mode == tables.modes['binary']:
            encoded = self.encode_bytes()
        elif self.mode == tables.modes['kanji']:
            encoded = self.encode_kanji()
        return encoded

    def encode_alphanumeric(self):
        """This method encodes the QR code's data if its mode is
        alphanumeric. It returns the data encoded as a binary string.
        """
        # Convert the string to upper case
        self.data = self.data.upper()

        # Change the data such that it uses a QR code ascii table
        ascii = []
        for char in self.data:
            if isinstance(char, int):
                ascii.append(tables.ascii_codes[chr(char)])
            else:
                ascii.append(tables.ascii_codes[char])

        # Now perform the algorithm that will make the ascii into bit fields
        with io.StringIO() as buf:
            for (a, b) in self.grouper(2, ascii):
                if b is not None:
                    buf.write(self.binary_string((45 * a) + b, 11))
                else:
                    # This occurs when there is an odd number
                    # of characters in the data
                    buf.write(self.binary_string(a, 6))

            # Return the binary string
            # print(buf.__repr__())  # @this one is create by udoy to see buf data.
            return buf.getvalue()

    def encode_numeric(self):
        """This method encodes the QR code's data if its mode is
        numeric. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            # Break the number into groups of three digits
            for triplet in self.grouper(3, self.data):
                number = ''
                for digit in triplet:
                    if isinstance(digit, int):
                        digit = chr(digit)

                    # Only build the string if digit is not None
                    if digit:
                        number = ''.join([number, digit])
                    else:
                        break

                # If the number is one digits, make a 4 bit field
                if len(number) == 1:
                    bin = self.binary_string(number, 4)

                # If the number is two digits, make a 7 bit field
                elif len(number) == 2:
                    bin = self.binary_string(number, 7)

                # Three digit numbers use a 10 bit field
                else:
                    bin = self.binary_string(number, 10)

                buf.write(bin)
            return buf.getvalue()

    def encode_bytes(self):
        """This method encodes the QR code's data if its mode is
        8 bit mode. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            for char in self.data:
                if not isinstance(char, int):
                    buf.write('{{0:0{0}b}}'.format(8).format(ord(char)))
                else:
                    buf.write('{{0:0{0}b}}'.format(8).format(char))
            return buf.getvalue()

    def encode_kanji(self):
        """This method encodes the QR code's data if its mode is
        kanji. It returns the data encoded as a binary string.
        """

        def two_bytes(data):
            """Output two byte character code as a single integer."""

            def next_byte(b):
                """Make sure that character code is an int. Python 2 and
                3 compatibility.
                """
                if not isinstance(b, int):
                    return ord(b)
                else:
                    return b

            # Go through the data by looping to every other character
            for i in range(0, len(data), 2):
                yield (next_byte(data[i]) << 8) | next_byte(data[i + 1])

        # Force the data into Kanji encoded bytes
        if isinstance(self.data, bytes):
            data = self.data.decode('shiftjis').encode('shiftjis')
        else:
            data = self.data.encode('shiftjis')

        # Now perform the algorithm that will make the kanji into 13 bit fields
        with io.StringIO() as buf:
            for asint in two_bytes(data):
                # Shift the two byte value as indicated by the standard
                if 0x8140 <= asint <= 0x9FFC:
                    difference = asint - 0x8140
                elif 0xE040 <= asint <= 0xEBBF:
                    difference = asint - 0xC140

                # Split the new value into most and least significant bytes
                msb = (difference >> 8)
                lsb = (difference & 0x00FF)

                # Calculate the actual 13 bit binary value
                buf.write('{0:013b}'.format((msb * 0xC0) + lsb))
            # Return the binary string
            return buf.getvalue()

    def add_data(self):
        """This function properly constructs a QR code's data string. It takes
        into account the interleaving pattern required by the standard.
        """
        # Encode the data into a QR code
        self.buffer.write(self.binary_string(self.mode, 8))
        self.buffer.write(self.get_data_length())
        self.buffer.write(self.encode())

        # Converts the buffer into "code word" integers.
        # The online debugger outputs them this way, makes
        # for easier comparisons.
        """this block uncomment to see buffer value"""  # a
        s = self.buffer.getvalue()
        # for i in range(0, len(s), 8):
            # print(int(s[i:i+8], 2), end=',')
        # print()


        # I was performing the terminate_bits() part in the encoding.
        # As per the standard, terminating bits are only supposed to
        # be added after the bit stream is complete. I took that to
        # mean after the encoding, but actually it is after the entire
        # bit stream has been constructed.
        bits = self.terminate_bits(self.buffer.getvalue())
        if bits is not None:
            self.buffer.write(bits)

        # delimit_words and add_words can return None
        add_bits = self.delimit_words()
        if add_bits:
            self.buffer.write(add_bits)

        fill_bytes = self.add_words()
        if fill_bytes:
            self.buffer.write(fill_bytes)

        # Get a numeric representation of the data
        data = [int(''.join(x), 2)
                for x in self.grouper(8, self.buffer.getvalue())]

        # This is the error information for the code
        error_info = tables.eccwbi[self.version][self.error]                    #error = type of error correction level

        # This will hold our data blocks
        data_blocks = []

        # This will hold our error blocks
        error_blocks = []

        # Some codes have the data sliced into two different sized blocks
        # for example, first two 14 word sized blocks, then four 15 word
        # sized blocks. This means that slicing size can change over time.
        data_block_sizes = [error_info[2]] * error_info[1]
        if error_info[3] != 0:
            data_block_sizes.extend([error_info[4]] * error_info[3])

        # For every block of data, slice the data into the appropriate
        # sized block
        current_byte = 0
        for n_data_blocks in data_block_sizes:
            data_blocks.append(data[current_byte:current_byte + n_data_blocks])
            current_byte += n_data_blocks

        # I am not sure about the test after the "and". This was added to
        # fix a bug where after delimit_words padded the bit stream, a zero
        # byte ends up being added. After checking around, it seems this extra
        # byte is supposed to be chopped off, but I cannot find that in the
        # standard! I am adding it to solve the bug, I believe it is correct.
        if current_byte < len(data):
            raise ValueError('Too much data for this code version.')

        # DEBUG CODE!!!!
        # Print out the data blocks
        # print('Data Blocks:\n{0}'.format(data_blocks))  # seeing data bolck

        # Calculate the error blocks
        for n, block in enumerate(data_blocks):
            # print(f"value of n in enumareate {n} \nand value of block in enumarate{block}")
            error_blocks.append(self.make_error_block(block, n))

        # DEBUG CODE!!!!
        # Print out the error blocks
        # print('Error Blocks:\n{0}'.format(error_blocks))  # seeing error block

        # Buffer we will write our data blocks into
        data_buffer = io.StringIO()
        # print(f"only_buffer:{data_buffer.getvalue()}")                    #buffer is only created thats why its empty.
        # lsts see what data buffer hold.code by udoy.
        # print(f"data_buffer:{self.buffer.getvalue()}")
        # print(f"data_buffer length is: {len(self.buffer.getvalue())}")

        # Add the data blocks     to the data buffer.                                  #i think i need to add error block same way
        # Write the buffer such that: block 1 byte 1, block 2 byte 1, etc.
        largest_block = max(error_info[2], error_info[4]) + error_info[0]
        for i in range(largest_block):
            for block in data_blocks:
                if i < len(block):
                    data_buffer.write(self.binary_string(block[i], 8))

        # Add the error code blocks.
        # Write the buffer such that: block 1 byte 1, block 2 byte 2, etc.      on error block i need to tweek to make it work
        for i in range(error_info[0]):
            for block in error_blocks:
                data_buffer.write(self.binary_string(block[i], 8))

        #in here data_buffer value passed into global/class buffer value.
        self.buffer = data_buffer  # this is final buffer of the output holder
        dt_bf=[]
        dt_bf.append(data_buffer.getvalue())
        # print("data buff:",dt_bf)               #need to itter here to store obj value into list.
        # to see the fina data buffer.
        # print("final buffer value is :"+str(self.buffer.getvalue))              #need to read out buffer object.

    def terminate_bits(self, payload):
        """This method adds zeros to the end of the encoded data so that the
        encoded data is of the correct length. It returns a binary string
        containing the bits to be added.
        """
        data_capacity = tables.data_capacity[self.version][self.error][0]

        if len(payload) > data_capacity:
            raise ValueError('The supplied data will not fit '
                             'within this version of a QR code.')

        # We must add up to 4 zeros to make up for any shortfall in the
        # length of the data field.
        if len(payload) == data_capacity:
            return None
        elif len(payload) <= data_capacity - 4:
            bits = self.binary_string(0, 4)
        else:
            # Make up any shortfall need with less than 4 zeros
            bits = self.binary_string(0, data_capacity - len(payload))  # it add how much 0 data bit needed to add.

        return bits

    def delimit_words(self):
        """This method takes the existing encoded binary string
        and returns a binary string that will pad it such that
        the encoded string contains only full bytes.
        """
        bits_short = 8 - (len(self.buffer.getvalue()) % 8)

        # The string already falls on an byte boundary do nothing
        if bits_short == 0 or bits_short == 8:
            return None
        else:
            return self.binary_string(0, bits_short)

    def add_words(self):
        """The data block must fill the entire data capacity of the QR code.
        If we fall short, then we must add bytes to the end of the encoded
        data field. The value of these bytes are specified in the standard.
        """

        data_blocks = len(self.buffer.getvalue()) // 8
        total_blocks = tables.data_capacity[self.version][self.error][0] // 8
        # print total bolck size of the qr code to see how many block are available.
        # print(f"total block: {total_blocks}")
        needed_blocks = total_blocks - data_blocks

        if needed_blocks == 0:
            return None

        # This will return item1, item2, item1, item2, etc.
        block = itertools.cycle(['11101100', '00010001'])

        # Create a string of the needed blocks
        return ''.join([next(block) for x in range(needed_blocks)])

    def make_error_block(self, block, block_number):
        """This function constructs the error correction block of the
        given data block. This is *very complicated* process. To
        understand the code you need to read:

        """
        # Get the error information from the standards table
        error_info = tables.eccwbi[self.version][self.error]
        # print(f"error ver info {error_info}")
        # This is the number of 8-bit words per block
        if block_number < error_info[1]:
            code_words_per_block = error_info[2]
        else:
            code_words_per_block = error_info[4]

        # This is the size of the error block
        error_block_size = error_info[0]

        # Copy the block as the message polynomial coefficients
        mp_co = block[:]

        # Add the error blocks to themial message polyno
        mp_co.extend([0] * (error_block_size))

        # Get the generator polynomial
        generator = tables.generator_polynomials[error_block_size]

        # This will hold the temporary sum of the message coefficient and the
        # generator polynomial
        gen_result = [0] * len(generator)

        # Go through every code word in the block
        for i in range(code_words_per_block):
            # Get the first coefficient from the message polynomial
            coefficient = mp_co.pop(0)

            # Skip coefficients that are zero
            if coefficient == 0:
                continue
            else:
                # Turn the coefficient into an alpha exponent
                alpha_exp = tables.galois_antilog[coefficient]

            # Add the alpha to the generator polynomial
            for n in range(len(generator)):
                gen_result[n] = alpha_exp + generator[n]
                if gen_result[n] > 255:
                    gen_result[n] = gen_result[n] % 255

                # Convert the alpha notation back into coefficients
                gen_result[n] = tables.galois_log[gen_result[n]]

                # XOR the sum with the message coefficients
                mp_co[n] = gen_result[n] ^ mp_co[n]

        # Pad the end of the error blocks with zeros if needed
        if len(mp_co) < code_words_per_block:
            mp_co.extend([0] * (code_words_per_block - len(mp_co)))

        return mp_co
        # commented out make code

    def data_spliter(self, data):
        """this module split data in to 2 digit by 2 digit data block
        like : if i have a binary data of 16 digit that data going to split in to 8 group or list index.
        example: let assume binary_data= '0001001000010011'
        then this data i'm going to split in to 2 bit by 2 bit
        out put should be like this ="00","01","00","10","00","01","00","11"
        and finaly i returned this output of data that going to generate our final qr matrix value.
        """
        self.data = data
        # print(fr"data before splitting: {data}")
        n = 2
        splitted_data = [data[i:i + n] for i in range(0, len(data), n)]
        # print(len(splitted_data))
        # print(splitted_data)
        return splitted_data


"""test code part to see how generate qr matrix data."""


##############################################################################
##############################################################################
#
# Output Functions
#
##############################################################################
##############################################################################


def _text(matrix_value, quiet_zone=4):
    """This method returns a text based representation of the QR code.
    This is useful for debugging purposes.
    """
    buf = io.StringIO()

    border_row = '0 ' * (len(matrix_value[0]) + (quiet_zone * 2))

    # Every QR code start with a quiet zone at the top
    for b in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')

    for row in matrix_value:
        # Draw the starting quiet zone
        # print(f" single row vlaue row:{row}")
        for b in range(quiet_zone):
            buf.write('0 ')

        # Actually draw the QR code
        for bit in row:
            if bit == "00" or "0":
                buf.write('00')
            elif bit == "01" or "1":
                buf.write('01')
            elif bit == "10":
                buf.write('10')
            elif bit == "11":
                buf.write('11')

            # This is for debugging unfinished QR codes,
            # unset pixels will be spaces.
            else:
                buf.write('')

        # Draw the ending quiet zone
        for b in range(quiet_zone):
            buf.write('0 ')
        buf.write('\n')

    # Every QR code ends with a quiet zone at the bottom
    for b in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')

    return buf.getvalue()

def imageGen(code):
    """This function writes the QR code out as an SVG document. The
    code is drawn by drawing only the modules corresponding to a 1. They
    are drawn using a line, such that contiguous modules in a row
    are drawn with a single line. The file parameter is used to
    specify where to write the document to. It can either be a writable (binary)
    stream or a file path. The scale parameter is sets how large to draw
    a single module. By default one pixel is used to draw a single
    module. This may make the code to small to be read efficiently.
    Increasing the scale will make the code larger. This method will accept
    fractional scales (e.g. 2.5).

    """
    """
    @author: ababil islam udoy
    """

    la = code
    import numpy as np
    from PIL import Image, ImageOps
    import glob
    import os
# /home/ab/Desktop/QR/raw/img1.jpg
    path = os.path.dirname((os.path.abspath(__file__)))
    path= os.path.join(path, "raw")
    # print(path)

    # open images by providing path of images
    img1 = Image.open(os.path.join(path,"img1.jpg"))
    # img1 = Image.open("raw/img1.jpg")
    # img2 = Image.open("raw/img2.jpg")
    img2 = Image.open(os.path.join(path,"img2.jpg"))
    
    # img3 = Image.open("raw/img3.png")
    img3 = Image.open(os.path.join(path,"img3.png"))
    # img4 = Image.open("raw/img4.png")
    img4 = Image.open(os.path.join(path,"img4.png"))

    # ++++++++++++++++ gray scelling++++++++++++++++
    img1 = ImageOps.grayscale(img1)
    img2 = ImageOps.grayscale(img2)
    img3 = ImageOps.grayscale(img3)
    img4 = ImageOps.grayscale(img4)

    # +++++++++++++++image resize++++=
    img1 = img1.resize((50, 50))
    img2 = img2.resize((50, 50))
    img3 = img3.resize((50, 50))
    img4 = img4.resize((50, 50))

    # ++++++++image displaying +++++++
    # img1.show()
    # img2.show()
    # img3.show()
    # img4.show()

    # need to convert image in to numpy arrary
    img_array_1 = np.array(img1)
    img_array_2 = np.array(img2)
    img_array_3 = np.array(img3)
    img_array_4 = np.array(img4)

    z = np.zeros((50, 0))
    # print(len(la[1])*50+4)
    matrixsize = len(la[1]) * 50
    f = np.zeros((4, matrixsize))
    # z=[[]]
    # print(np.shape(z))
    # print(img_array_1)

    # x=[[]]         #need to assign numpy dynamic array.

    x = np.zeros((0, matrixsize))
    for i in range(len(la)):
        for j in range(len(la[i])):
            # print(j,end=",")
            val = la[i][j]
            value = int(val)
            # print("value:{}  ,type {}".format(value, type(value)))
            if value == 0:
                z = np.append(z, img_array_1, axis=1)
                # z.append(img_array_1)
            elif value == 1:
                z = np.append(z, img_array_2, axis=1)

            elif value == 10:
                z = np.append(z, img_array_3, axis=1)

            elif value == 11:
                z = np.append(z, img_array_4, axis=1)
        # x.append(z)
        x = np.append(x, z, axis=0)
        # z=[[]]
        z = np.zeros((50, 0))
    # z.show()

    # print(type(x))
    # print(np.shape(z))
    # new_x= x.convert('RGB')
    # finalImage = Image.fromarray(x)
    # finalImage.show()

    # print(np.shape(z))

    # finalImage.save('generated_image.png')

    x = x / 255
    # for horigontal adjustment of border,
    # print(type(x))
    s = np.shape(x)
    v = s[0]
    # print(v)
    tl = np.ones((v, 50))  # white tag tl=left tr=tag right
    tr = np.ones((v, 50))
    hl = np.hstack((tl, x))
    hr = np.hstack((hl, tr))
    # for vertical adjustment with white border
    # print(type(hr))
    s = np.shape(hr)
    vt = s[1]
    # print(vt)
    tv = np.ones((50, vt))  # matrix with one
    vu = np.vstack((tv, hr))
    vd = np.vstack((vu, tv))
    fr = vd * 255
    # convert numpy array to image object
    finalImage = Image.fromarray(fr)
    # to show image
    # finalImage.show()
    #
    # finalImage.save("4QR.jpeg")

    import imageio
    imageio.imwrite('4_state_QR.jpeg', finalImage)
    print(" ")
    print("Image generation process successful.")

