from __future__ import absolute_import, division, print_function, with_statement, unicode_literals
import idna
import tables
import builder

try:
    # string = idna.Unicode  # Python 2 use idna to convert unicode mode 2 to 3
    pass
except NameError:
    pass


def create(content, error='l', version=None, mode=None, encoding=None):
    """When creating a Four States QR code only the content to be encoded is required,
    all the other properties of the code will be guessed based on the
    contents given. This function will return a :class:`QRCode` object.

    Unless you are familiar with QR code's inner workings
    it is recommended that you just specify the *content* and nothing else.
    However, there are cases where you may want to specify the various
    properties of the created code manually, this is what the other
    parameters do. Below, you will find a lengthy explanation of what
    each parameter is for. Note, the parameter names and values are taken
    directly from the standards. You may need to familiarize yourself
    with the terminology of QR codes for the names and their values to
    make sense.

    The *error* parameter sets the error correction level of the code. There
    are four levels defined by the standard. The first is level 'L' which
    allows for 7% of the code to be corrected. Second, is level 'M' which
    allows for 15% of the code to be corrected. Next, is level 'Q' which
    is the most common choice for error correction, it allow 25% of the
    code to be corrected. Finally, there is the highest level 'H' which
    allows for 30% of the code to be corrected. There are several ways to
    specify this parameter, you can use an upper or lower case letter,
    a float corresponding to the percentage of correction, or a string
    containing the percentage. See tables.modes for all the possible
    values. By default this parameter is set to 'H' which is the highest
    possible error correction, but it has the smallest available data
    capacity.

    The *version* parameter specifies the size and data capacity of the
    code. Versions are any integer between 1 and 40. Where version 1 is
    the smallest QR code, and version 40 is the largest. If this parameter
    is left unspecified, then the contents and error correction level will
    be used to guess the smallest possible QR code version that the
    content will fit inside of. You may want to specify this parameter
    for consistency when generating several QR codes with varying amounts
    of data. That way all of the generated codes would have the same size.

    The *mode* parameter specifies how the contents will be encoded. By
    default, the best possible mode for the contents is guessed. There
    are four possible modes. First, is 'numeric' which is
    used to encode integer numbers. Next, is 'alphanumeric' which is
    used to encode some ASCII characters. This mode uses only a limited
    set of characters. Most problematic is that it can only use upper case
    English characters, consequently, the content parameter will be
    subjected to str.upper() before encoding. See tables.ascii_codes for
    a complete list of available characters. The is 'kanji' mode can be
    used for Japanese characters, but only those that can be understood
    via the shift-jis string encoding. Finally, we then have 'binary' mode
    which just encodes the bytes directly into the QR code (this encoding
    is the least efficient).
    The *encoding* parameter specifies how the content will be interpreted.
    This parameter only matters if the *content* is a string, unicode, or
    byte array type. This parameter must be a valid encoding string or None.
    t will be passed the *content*'s encode/decode methods.
    """
    # QRCode(content, error, version, mode, encoding)
    return QRCode(content, error, version, mode, encoding)  # this one commented out and add code in upperline


class QRCode:
    """This class represents a QR code. To use this class simply give the
    constructor a string representing the data to be encoded, it will then
    build a code in memory. You can then save it in various formats. Note,
    codes can be written out as PNG files but this requires the PyPNG module.
    You can find the PyPNG module at https://packages.python.org/pypng/.

    Examples:
        # >>> from _4_stg_qr import QRCode
        # >>> import sys
        # >>> url = QRCode('http://AB')
        # >>> image = url.image_generation()


    .. note::
        For what all of the parameters do, see the :func:`_4stg_qr.create`
        function.
    """

    def __init__(self, content, error='L', version=None, mode=None,
                 encoding='iso-8859-1'):
        # Guess the mode of the code, this will also be used for
        # error checking
        guessed_content_type, encoding = self._detect_content_type(content, encoding)

        if encoding is None:
            encoding = 'iso-8859-1'

        # Store the encoding for use later
        if guessed_content_type == 'kanji':
            self.encoding = 'shiftjis'
        else:
            self.encoding = encoding

        if version is not None:
            if 1 <= version <= 40:
                self.version = version
            else:
                raise ValueError("Illegal version {0}, version must be between "
                                 "1 and 40.".format(version))

        # Decode a 'byte array' contents into a string format
        if isinstance(content, bytes):
            self.data = content.decode(encoding)
            print("data inside instance:" + self.data)
        # Give a string an encoding
        elif hasattr(content, 'encode'):
            self.data = content.encode(self.encoding)
            print("data:" + self.data.__repr__())
        # The contents are not a byte array or string, so
        # try naively converting to a string representation.
        else:
            self.data = str(content)  # str == unicode in Py 3.x, or string(content) in py 2.x see file head
            # print("data inside else:" + self.data.__repr__())
        # Force a passed in mode to be lowercase
        if hasattr(mode, 'lower'):
            mode = mode.lower()

        # Check that the mode parameter is compatible with the contents
        if mode is None:
            # Use the guessed mode
            self.mode = guessed_content_type
            self.mode_num = tables.modes[self.mode]
        elif mode not in tables.modes.keys():
            # Unknown mode
            raise ValueError('{0} is not a valid mode.'.format(mode))
        elif guessed_content_type == 'binary' and \
                tables.modes[mode] != tables.modes['binary']:
            # Binary is only guessed as a last resort, if the
            # passed in mode is not binary the data won't encode
            raise ValueError('The content provided cannot be encoded with '
                             'the mode {}, it can only be encoded as '
                             'binary.'.format(mode))
        elif tables.modes[mode] == tables.modes['numeric'] and \
                guessed_content_type != 'numeric':
            # If numeric encoding is requested make sure the data can
            # be encoded in that format
            raise ValueError('The content cannot be encoded as numeric.')
        elif tables.modes[mode] == tables.modes['kanji'] and \
                guessed_content_type != 'kanji':
            raise ValueError('The content cannot be encoded as kanji.')
        else:
            # The data should encode with the passed in mode
            self.mode = mode
            self.mode_num = tables.modes[self.mode]

        # Check that the user passed in a valid error level
        if error in tables.error_level.keys():
            self.error = tables.error_level[error]
        else:
            raise ValueError('{0} is not a valid error '
                             'level.'.format(error))

        # Guess the "best" version
        self.version = self._pick_best_fit(self.data)

        # If the user supplied a version, then check that it has
        # sufficient data capacity for the contents passed in
        if version:
            if version >= self.version:
                self.version = version
            else:
                raise ValueError('The data will not fit inside a version {} '
                                 'code with the given encoding and error '
                                 'level (the code must be at least a '
                                 'version {}).'.format(version, self.version))

        # Build the QR code
        self.builder = builder.QRCodeBuilder(data=self.data,
                                             version=self.version,
                                             mode=self.mode,
                                             error=self.error)

        # Save the code for easier reference
        self.finalMatrix = self.builder.final_gen_matrix

    #     test part 19/10/21

    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "QRCode(content={0}, error='{1}', version={2}, mode='{3}')" \
            .format(repr(self.data), self.error, self.version, self.mode)

    def _detect_content_type(self, content, encoding):
        """This method tries to auto-detect the type of the data. It first
        tries to see if the data is a valid integer, in which case it returns
        numeric. Next, it tests the data to see if it is 'alphanumeric.' QR
        Codes use a special table with very limited range of ASCII characters.
        The code's data is tested to make sure it fits inside this limited
        range. If all else fails, the data is determined to be of type
        'binary.'

        Returns a tuple containing the detected mode and encoding.

        Note, encoding ECI is not yet implemented.
        """

        def two_bytes(c):
            """Output two byte character code as a single integer."""

            def next_byte(b):
                """Make sure that character code is an int. Python 2 and 3 compatibility."""
                if not isinstance(b, int):
                    """ord() method accepts a single character.
                     and returned the numerical Unicode value of the character as a response"""
                    return ord(b)
                else:
                    return b

            # Go through the data by looping to every other character
            for i in range(0, len(c), 2):
                yield (next_byte(c[i]) << 8) | next_byte(c[i + 1])

        # to See if the data is a number
        try:
            if str(content).isdigit():
                return 'numeric', encoding
        except (TypeError, UnicodeError):
            pass

        # See if that data is alphanumeric based on the standards
        # special ASCII table
        valid_characters = ''.join(tables.ascii_codes.keys())

        # Force the characters into a byte array
        valid_characters = valid_characters.encode('ASCII')

        try:
            if isinstance(content, bytes):
                c = content.decode('ASCII')
            else:
                c = str(content).encode('ASCII')

            if all(map(lambda x: x in valid_characters, c)):
                return 'alphanumeric', 'ASCII'

        # This occurs if the content does not contain ASCII characters.
        # Since the whole point of the if statement is to look for ASCII
        # characters, the resulting mode should not be alphanumeric.
        # Hence, this is not an error.
        except TypeError:
            pass
        except UnicodeError:
            pass

        try:
            if isinstance(content, bytes):
                if encoding is None:
                    encoding = 'shiftjis'

                c = content.decode(encoding).encode('shiftjis')
            else:
                c = content.encode('shiftjis')

            # All kanji characters must be two bytes long, make sure the
            # string length is not odd.
            if len(c) % 2 != 0:
                return 'binary', encoding

            # Make sure the characters are actually in range.
            for as_int in two_bytes(c):
                # Shift the two byte value as indicated by the standard
                if not (0x8140 <= as_int <= 0x9FFC or 0xE040 <= as_int <= 0xEBBF):
                    return 'binary', encoding

            return 'kanji', encoding

        except UnicodeError:
            # This occurs if the content does not contain Shift JIS kanji
            # characters. Hence, the resulting mode should not be kanji.
            # This is not an error.
            pass

        # if all of the other attempts failed. The content can only be binary.
        return 'binary', encoding

    def _pick_best_fit(self, content):
        """This method return the smallest possible QR code version number
        that will fit the specified data with the given error level.
        """
        import math

        for version in range(1, 41):
            # Get the maximum possible capacity
            capacity = tables.data_capacity[version][self.error][self.mode_num]

            # Check the capacity
            # Kanji's count in the table is "characters" which are two bytes
            if (self.mode_num == tables.modes['kanji'] and
                    capacity >= math.ceil(len(content) / 2)):
                return version
            if capacity >= len(content):
                return version

        raise ValueError('The data will not fit in any QR code version '
                         'with the given encoding and error level.')

    ######################################################################################################
    ####                       display output part                                #############
    ######################################################################################################
    # def text(self, quiet_zone=4):
    #     """This method returns a string based representation of the QR code.
    #     The data modules are represented by 1's and the background modules are
    #     represented by 0's. The main purpose of this method is to act a
    #     starting point for users to create their own renderers.
    #
    #     The *quiet_zone* parameter sets how wide the quiet zone around the code
    #     should be. According to the standard this should be 4 modules. It is
    #     left settable because such a wide quiet zone is unnecessary in many
    #     applications.
    #
    #     Example:
    #         # >>> code = pyqrcode.create('Example')
    #         # >>> text = code.text()
    #         # >>> print(text)
    #     """
    #     return builder._text(self.finalMatrix, quiet_zone)

    def image_generation(self):
        """
        Example:
        # >>> code = init.create('Example')
        
        """
        return builder.imageGen(self.finalMatrix)