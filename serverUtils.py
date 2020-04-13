class Utils:

    # -------------------------------
    # DISPLAY CONSTANTS
    #-------------------------------
    DEBUG = True

    #-------------------------------
    # COLOR CONSTANTS
    #-------------------------------
    BOLD      = "BOLD"
    UNDERLINE = "UNDERLINE"
    NORMAL    = "NORMAL"
    RED       = "RED"
    GREEN     = "GREEN"
    YELLOW    = "YELLOW"
    BLUE      = "BLUE"

    #-------------------------------
    # COLOR STRUCTURES
    #-------------------------------
    STYLES = {
        BOLD     : '\033[1m',
        UNDERLINE: '\033[4m',
    }

    COLORS = {
        NORMAL : '\033[0m' ,
        RED    : '\033[31m',
        GREEN  : '\033[92m',
        YELLOW : '\033[93m',
        BLUE   : '\033[94m',
    }


    #-------------------------------
    # COLOR FUNCTIONS
    #-------------------------------
    @staticmethod
    def getClrStr(s,clr="NORMAL",style=None):
        # Prepare output
        out = ""
        # Check if style is ok and add it
        if style in Utils.STYLES:
            out += Utils.STYLES[style]
        # Check if color is ok and add it
        if clr in Utils.COLORS:
            out += Utils.COLORS[clr]
        # Add string
        out += str(s)
        # Set to normal font
        out += Utils.COLORS["NORMAL"]
        # return result
        return out

    #-------------------------------
    # DISPLAY TEXT FUNCTIONS
    #-------------------------------
    @staticmethod
    def log(s):
        if Utils.DEBUG:
            print(s)

    # -------------------------------
    # COMMAND FUNCTIONS
    # -------------------------------
    @staticmethod
    def getDisplayRequest():
        msg = "list"
        return msg.encode()
    @staticmethod
    def getEndRequest():
        msg = "exit()"
        return msg.encode()



