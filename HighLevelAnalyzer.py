# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer.
    my_string_setting = StringSetting()
    my_number_setting = NumberSetting(min_value=0, max_value=100)
    my_choices_setting = ChoicesSetting(choices=('A', 'B'))

    pumpReplyRowCount = 0
    aircraftReplyRowCount = 0
    rowStore = ""
    unknownStore = ""
    previousFrameValue = ""
    toggler = 0

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'mytype': {
            'format': '= {{data.input_type}} ='
        }
    }

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        print("Settings:", self.my_string_setting,
              self.my_number_setting, self.my_choices_setting)

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        printUnknownZeros = False
        printUnknownData = False
        printAircraftFrames = True
        printPumpFrames = True

        currentFrameValue = frame.data['data'].hex()
        # print("current frame val",currentFrameValue)
        if self.previousFrameValue == "55" and currentFrameValue == "16":
            # aircraft message
            # print("aircraft frame")
            self.toggler = 1
        if self.previousFrameValue == "55" and currentFrameValue == "1c":
            # pump message
            # print("pump frame")
            self.toggler = 2

        if self.toggler == 0:  # for unknown data storing
            self.unknownStore = self.unknownStore + self.previousFrameValue + ","
            if self.previousFrameValue != "00":
                if printUnknownData == True:
                    print("Unknown useful data: " + self.previousFrameValue)
        if self.toggler != 0 and self.unknownStore != "":  # for unknown data printing
            if printUnknownZeros == True:
                print("Unknown data: " + self.unknownStore)
            self.unknownStore = ""

        if self.toggler == 1:  # aircraft data processing
            self.aircraftReplyRowCount = self.aircraftReplyRowCount + 1
            # 10 && 16 are slow rate increase vales that range 6 to 9 on two motors then back from 6 to 9 when 4 motors
            # if self.aircraftReplyRowCount == 8 or self.aircraftReplyRowCount == 9 or self.aircraftReplyRowCount == 10  or self.aircraftReplyRowCount == 14 or self.aircraftReplyRowCount == 15 or self.aircraftReplyRowCount == 21 or self.aircraftReplyRowCount == 22: # filter changing values and convert to decimal
            #    modifiedOutput = str(int(self.previousFrameValue,16))
            #    if int(self.previousFrameValue,16) < 100:
            #        modifiedOutput = " " + str(int(self.previousFrameValue,16))
            #    if int(self.previousFrameValue,16) < 10:
            #        modifiedOutput = "  " + str(int(self.previousFrameValue,16))
            #    self.rowStore = self.rowStore + modifiedOutput + ","
            # else: #do not modify, just save unfiltered values
            self.rowStore = self.rowStore + self.previousFrameValue + ","
            # self.rowStore = rowStore + str(int(csvStore[i], 16)) + ","
            if self.aircraftReplyRowCount == 22:
                if printAircraftFrames == True:
                    output = self.rowStore
                    frameCheck = self.previousFrameValue
                    if frameCheck == "11":
                        print("AIRC", output, "ALL PUMPS OFF")
                    elif frameCheck == "53":
                        print("AIRC", output, "PUMP RUNNING")
                    elif frameCheck == "83":
                        print("AIRC", output, "PUMP DISABLED")
                    elif frameCheck == "a0":
                        print("AIRC", output, "MINIMUM SPRAY")
                    else:
                        print("AIRC", output, "Unknown: " + frameCheck)

                ##print("end found")
                self.toggler = 0
                self.rowStore = ""
                self.aircraftReplyRowCount = 0

        if self.toggler == 2:  # pump data processing
            self.pumpReplyRowCount = self.pumpReplyRowCount + 1
            self.rowStore = self.rowStore + self.previousFrameValue + ","
            # self.rowStore = self.rowStore + str(int(csvStore[i], 16)) + ","
            if self.pumpReplyRowCount == 28:
                if printPumpFrames == True:
                    output = self.rowStore
                    print("PUMP", output)
                self.toggler = 0
                self.pumpReplyRowCount = 0
                self.rowStore = ""

        self.previousFrameValue = currentFrameValue

        # Return the data frame itself
        return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
            'input_type': "DEC: " + str(int(currentFrameValue,16)) + "  HEX: 0x"+ currentFrameValue,
        })
