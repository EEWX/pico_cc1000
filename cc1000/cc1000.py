from machine import SPI,UART,Pin,ADC
from micropython import const
import utime as time

class cc1000:
    FREQ_A = 0
    FREQ_B = 1
    FREQ_REF = 0
    TX = 1
    RX = 0
    REG_MAIN = const(0x00)
    #rx frequency
    REG_FREQ_2A = const(0x01)
    REG_FREQ_1A = const(0x02)
    REG_FREQ_0A = const(0x03)
    #tx frequency
    REG_FREQ_2B = const(0x04)
    REG_FREQ_1B = const(0x05)
    REG_FREQ_0B = const(0x06)
    REG_FSEP1 = const(0x07)
    REG_FSEP0 = const(0x08)
    REG_CURRENT = const(0x09)
    REG_FRONT_END = const(0x0A)
    REG_PA_POW = const(0x0B)
    REG_PLL = const(0x0C)
    REG_LOCK = const(0x0D)
    REG_CAL = const(0x0E)
    REG_MODEM2 = const(0x0F)
    REG_MODEM1 = const(0x10)
    REG_MODEM0 = const(0x11)
    REG_MATCH = const(0x12)
    REG_FSCTRL = const(0x13)
    REG_PRESCALER = const(0x1C)
    buf = [20]
    def __init__(self,spi, cs, uart, rssi, freq, power):
        self.spi_rate = 500 * 1000
        self.uart_rate = 9600
        self.spi=spi
        self.uart=uart
        self.rssi=rssi
        self.cs=cs
        self.freq=freq
        self.power=power
        self.cs.init(cs.OUT, value=1)
        self.spi.init(baudrate=self.spi_rate, polarity=1, phase=0)
        self.reset()
       # self.uart.init(baudrate=self.uart_rate, tx=Pin(0),rx=Pin(1))
    def read_rssi(self):
        return(self.issi.read_u16())
    def tx_data(self):
        pass
    def rx_data(self):
        pass
    def write_reg(self,adr,cmd):
        #self.spi.init(baudrate=self.spi_rate, polarity=0, phase=0)
        self.cs(0)
        adr1=adr<<1 | 0x01#write mode
        self.spi.write(bytearray([adr1]))
        self.cs(1)
        self.spi.write(bytearray([cmd]))
        print("SPI write", hex(adr1), hex(cmd))
    def write_data(self,buf):
        #self.uart.init(baudrate=self.uart_rate, tx=Pin(0),rx=Pin(1))
        self.uart.write(bytearray([buf]))
    def set_power(self, power):
        if power>255 or power<0:
            print("Power input need to be in the range of 0-255!")
        else:
            self.write_reg(REG_PA_POW,power)#self. need to be added before the function
            print("Power has been set to:", power)
    def set_mode(self, mode):
        if mode is self.RX:
            self.write_reg(REG_MAIN,0x11)
            print("Rx mode entered")
        elif mode is self.TX:
            self.write_reg(REG_MAIN,0xc1)
            print("Tx mode entered")
        else:
            print("Only rx or tx can be selected")
    def reset(self):
        self.write_reg(REG_MAIN,0x3e)
        self.write_reg(REG_MAIN,0x3f)
        print("cc100 reset released")
    def set_freq(self, slot, freq):
        self.write_reg(REG_MODEM0,0x57)#Manchester mode, crystal 14.7456MHz
        print("UART mode, crystal range 12 to 16MHz")
        self.write_reg(REG_PLL,0x7B)#crystal divided by 7, Fref = 14.7456/7 = 2.1065MHz
        print("PLL clock divider set to 7")
        self.FREQ_REF = 14745600/7
        freq_reg = int((freq*16384)/self.FREQ_REF-8192)
        freq_actual = (freq_reg+8192)*self.FREQ_REF/16384
        freq_reg_byte = freq_reg.to_bytes(3,'big')
        if slot is self.FREQ_A:
            self.write_reg(REG_FREQ_2A,freq_reg_byte[0])
            self.write_reg(REG_FREQ_1A,freq_reg_byte[1])
            self.write_reg(REG_FREQ_0A,freq_reg_byte[2])
            print("Rx frequency", freq_actual,"Hz")
        elif slot is self.FREQ_B:
            self.write_reg(REG_FREQ_2B,freq_reg_byte[0])
            self.write_reg(REG_FREQ_1B,freq_reg_byte[1])
            self.write_reg(REG_FREQ_0B,freq_reg_byte[2])
            print("Tx frequency", freq_actual,"Hz")
        else:
            print("Only FREQ_A or FREQ_B can be selected")
    def cal(self):
        self.write_reg(REG_CAL,0xF5)#Calibration starts
        time.sleep_ms(40) # sleep for 40 milliseconds
        self.write_reg(REG_CAL,0x75)#Calibration starts
        print("Dual calibration done!")
    def set_current(self,vco,lo,pa):
        self.write_reg(REG_CURRENT,0x43)#Calibration starts
        print("Set VCO current to", vco,"LO current to",lo,"PA current to",pa)
        
spi0 = SPI(0)
uart0 = UART(0)
led = Pin(25)
led.init(led.OUT,value =0)
adc0 = ADC(26)
time.sleep_ms(500) # sleep for 40 milliseconds
led(1)
time.sleep_ms(500) # sleep for 40 milliseconds
led(0)
time.sleep_ms(500) # sleep for 40 milliseconds
led(1)
cc_rf1 = cc1000(spi0,Pin(5),uart0,adc0,433000000,10)
cc_rf1.set_power(254)
cc_rf1.set_freq(cc1000.FREQ_A,433000000)
cc_rf1.set_freq(cc1000.FREQ_B,400000000)
cc_rf1.cal()
cc_rf1.set_current(10,2,2)
cc_rf1.set_mode(cc_rf1.TX)