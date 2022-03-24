import tables
import io
import itertools
import math


class generator:
    """ this class is going to generte qr code cell value"""

    def __init__(self, generated_data, version, mode, error):
        # def __init__(self, getvalue, version, mode, error):
        # self.getvalue = getvalue
        self.generated_data = generated_data
        self.version = version
        self.mode = mode
        self.error = error
        from copy import deepcopy

        # test to see if the generated data == splited or not.
        # its very important to match generated data with splited data.
        # print(fr"generated_data:{generated_data}")
        # Get the size of the underlying matrix
        matrix_size = tables.version_size[self.version]

        # Create a template matrix we will build the codes with
        row = [' ' for x in range(matrix_size)]
        template = [deepcopy(row) for x in range(matrix_size)]
        # print(matrix_size)
        # Add mandatory information to the template
        self.add_detection_pattern(template)
        self.add_position_pattern(template)
        self.add_version_pattern(template)

        # udoy need to remove this mask part.
        # Create the various types of masks of the template
        # self.masks = self.make_masks(template)  # note comment the mask part to see what happend

        # new code 31/10/2021 added
        # self.add_final_pattern(template, matrix_size)                                     #comment out to see blow
        # udoy need to remove this mask part.
        # Create the various types of masks of the template
        # self.masks = self.make_masks(template)  # note comment the mask part to see what happend

        # self.best_mask = self.choose_best_mask()
        # self.code = self.masks
        matrix = self.add_final_pattern(template, matrix_size)
        self.final_matrix = matrix[0]
        self.final_matrix_size = len(matrix[0])
        # print(f"final matrix size:{self.final_matrix_size}*{self.final_matrix_size}")




        """code that run the generator module of qr data in qr"""

    def add_detection_pattern(self, template_matrix):
        """This method add the detection patterns to the QR code. This lets
        the scanner orient the pattern. It is required for all QR codes.
        The detection pattern consists of three boxes located at the upper
        left, upper right, and lower left corners of the matrix. Also, two
        special lines called the timing pattern is also necessary. Finally,
        a single black pixel is added just above the lower left black box.
        """

        # Draw outer black box
        for i in range(7):
            inv = -(i + 1)
            for j in [0, 6, -1, -7]:
                template_matrix[j][i] = 1
                template_matrix[i][j] = 1
                template_matrix[inv][j] = 1
                template_matrix[j][inv] = 1

        # Draw inner white box
        for i in range(1, 6):
            inv = -(i + 1)
            for j in [1, 5, -2, -6]:
                template_matrix[j][i] = 0
                template_matrix[i][j] = 0
                template_matrix[inv][j] = 0
                template_matrix[j][inv] = 0

        # Draw inner black box
        for i in range(2, 5):
            for j in range(2, 5):
                inv = -(i + 1)
                template_matrix[i][j] = 1
                template_matrix[inv][j] = 1
                template_matrix[j][inv] = 1

        # Draw white border
        for i in range(8):
            inv = -(i + 1)
            for j in [7, -8]:
                template_matrix[i][j] = 0
                template_matrix[j][i] = 0
                template_matrix[inv][j] = 0
                template_matrix[j][inv] = 0

            # To keep the code short, it draws an extra box
            # in the lower right corner, this removes it.
            for i in range(-8, 0):
                for j in range(-8, 0):
                    template_matrix[i][j] = ' '

            # Add the timing pattern
            bit = itertools.cycle([1, 0])
            for i in range(8, (len(template_matrix) - 8)):
                b = next(bit)
                template_matrix[i][6] = b
                template_matrix[6][i] = b

            # Add the extra black pixel
            template_matrix[-8][8] = 1

        """detection patter is ok. code review done."""
        """not using this feature in qr code right now it needed in future."""

    def add_position_pattern(self, m):
        """This method draws the position adjustment patterns onto the QR
        Code. All QR code versions larger than one require these special boxes
        called position adjustment patterns.
        """
        # Version 1 does not have a position adjustment pattern
        if self.version == 1:
            return

        # Get the coordinates for where to place the boxes
        coordinates = tables.position_adjustment[self.version]

        # Get the max and min coordinates to handle special cases
        min_coord = coordinates[0]
        max_coord = coordinates[-1]

        # Draw a box at each intersection of the coordinates
        for i in coordinates:
            for j in coordinates:
                # Do not draw these boxes because they would
                # interfere with the detection pattern
                if (i == min_coord and j == min_coord) or \
                        (i == min_coord and j == max_coord) or \
                        (i == max_coord and j == min_coord):
                    continue

                # Center black pixel
                m[i][j] = 1

                # Surround the pixel with a white box
                for x in [-1, 1]:
                    m[i + x][j + x] = 0
                    m[i + x][j] = 0
                    m[i][j + x] = 0
                    m[i - x][j + x] = 0
                    m[i + x][j - x] = 0

                # Surround the white box with a black box
                for x in [-2, 2]:
                    for y in [0, -1, 1]:
                        m[i + x][j + x] = 1
                        m[i + x][j + y] = 1
                        m[i + y][j + x] = 1
                        m[i - x][j + x] = 1
                        m[i + x][j - x] = 1
        #
        """version pattern"""

    def add_version_pattern(self, template_matrix):
        """For QR codes with a version 7 or higher, a special pattern
        specifying the code's version is required.

        For further information see:
        http://www.thonky.com/qr-code-tutorial/format-version-information/#example-of-version-7-information-string
        """
        if self.version < 7:
            return

        # Get the bit fields for this code's version
        # We will iterate across the string, the bit string
        # needs the least significant digit in the zero-th position
        field = iter(tables.version_pattern[self.version][::-1])

        # Where to start placing the pattern
        start = len(template_matrix) - 11

        # The version pattern is pretty odd looking
        for i in range(6):
            # The pattern is three modules wide
            for j in range(start, start + 3):
                bit = int(next(field))

                # Bottom Left
                template_matrix[i][j] = bit

                # Upper right
                template_matrix[j][i] = bit

    def add_final_pattern(self, template, matrix_size):
        """This method generates all seven masks so that the best mask can
        be determined. The template parameter is a code matrix that will
        server as the base for all the generated masks.
        """
        # matrix_size=matrix_size
        # print(f"matrix size is{matrix_size}")
        from copy import deepcopy
        # nmasks = len(tables.mask_patterns)                    #this n mask output 8
        # print("nmask:",nmasks)
        nmasks = 1
        masks = [''] * nmasks
        count = 0

        for n in range(nmasks):
            cur_pattern = deepcopy(template)
            # print("current mask",cur_pattern)
            masks[n] = cur_pattern
            # Add the type pattern bits to the code     need to modify the code
            self.add_type_pattern(cur_pattern, tables.type_bits[self.error][n])
            self.data_placer(cur_pattern, matrix_size,generated_data=self.generated_data)


        # DEBUG CODE!!!
        # Save all of the masks as png files
        # for i, m in enumerate(masks):
        #    _png(m, self.version, 'mask-{0}.png'.format(i), 5)
        # below line used for to checking single index value
        # print(masks)
        return masks

    # i dnt need to chose best mask.
    # this section of code place with adjestement patter that is big 7*7 matrix.
    """type pattern"""

    def add_type_pattern(self, m, type_bits):
        """This will add the pattern to the QR code that represents the error
        level.
        """
        field = iter(type_bits)
        for i in range(7):
            bit = int(next(field))

            # Skip the timing bits
            if i < 6:
                m[8][i] = bit
            else:
                m[8][i + 1] = bit

            if -8 < -(i + 1):
                m[-(i + 1)][8] = bit

        for i in range(-8, 0):
            bit = int(next(field))

            m[8][i] = bit

            i = -i
            # Skip timing column
            if i > 6:
                m[i][8] = bit
            else:
                m[i - 1][8] = bit

    # no need to improve any thing in add type pattern.
    def data_placer(self, cur_pattern, matrix_size, generated_data):
        self.generated_data=generated_data

        # print(self.generated_data)
        # bits = iter(self.generated_data)
        # print("itterable bit :", next(bits))
        # print("itterable bit :", next(bits))
        # print("itterable bit :", next(bits))

        # ab = generated_data.pop()
        # print(ab)
        row = matrix_size - 1
        max_itteration = matrix_size * matrix_size
        # print(f"data:{max_itteration}")
        # comment out after checking reversed data printing
        # for i in range(row,-1,-1):
        #     print(f"{i}")
        #     # matrix_size-=1
        # print("emd")

        #         placing data in list
        # bit = next(bits)
        for i in range(max_itteration):
            # print(i, end=" ")
            pass
            # print(bit)
        row_start = itertools.cycle([len(cur_pattern) - 1, 0])
        row_stop = itertools.cycle([-1, len(cur_pattern)])
        direction = itertools.cycle([-1, 1])
        # The data pattern is added using pairs of columns
        for column in range(len(cur_pattern) - 1, 0, -2):

            # The vertical timing pattern is an exception to the rules,
            # move the column counter over by one
            if column <= 6:
                column = column - 1

            # This will let us fill in the pattern
            # right-left, right-left, etc.
            column_pair = itertools.cycle([column, column - 1])  # collumn pair hold max_col and max-1_col
            # to see column_pair value
            # print(f"column_pair value:{next(column_pair)}")
            # Go through each row in the pattern moving up, then down
            for row in range(next(row_start), next(row_stop),
                             next(direction)):
                # bit = int(next(bits))
                # Fill in the right then left column
                for i in range(2):
                    col = next(column_pair)
                    # to see the column pair value how they come in col.
                    # print(f"columen:{col}")
                    # Go to the next column if we encounter a preexisting pattern (usually an alignment pattern)

                    # test code
                    if cur_pattern[row][col] != ' ':
                        continue

                    if len(generated_data) != 0:
                        ab = generated_data.pop(0)
                    else:
                        ab = "00"

                    # to see the type of data.
                    # print(type(ab))

                    cur_pattern[row][col] = ab

        # for i in range(0, row):
        #     print(cur_mask[i])
        return cur_pattern




