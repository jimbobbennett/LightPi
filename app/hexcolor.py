class HexColor:

    def __init__(self, hex_string):
        r = '0x' + hex_string[0:2]
        g = '0x' + hex_string[2:4]
        b = '0x' + hex_string[4:6]

        self.r = int(r, 0)
        self.g = int(g, 0)
        self.b = int(b, 0)

        self.rgb = (self.r, self.g, self.b)
