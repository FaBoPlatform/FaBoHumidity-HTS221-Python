# coding: utf-8
## @package FaBoHumidity_HTS221
#  This is a library for the FaBo Humidity I2C Brick.
#
#  http://fabo.io/208.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import smbus
import time

## I2C Slave Address
SLAVE_ADDRESS = 0x5F

## Device Search Reg
DEVICE_REG    = 0x0F

## Who am i device identifier
DEVICE_ID     = 0xBC

# AV_CONF:AVGH
# Averaged humidity samples configuration
AVGH_4    = 0b00000000
AVGH_8    = 0b00000001
AVGH_16   = 0b00000010
AVGH_32   = 0b00000011 # defalut
AVGH_64   = 0b00000100
AVGH_128  = 0b00000101
AVGH_256  = 0b00000110
AVGH_512  = 0b00000111

# AV_CONF:AVGT
# Averaged temperature samples configuration
AVGT_2    = 0b00000000
AVGT_4    = 0b00001000
AVGT_8    = 0b00010000
AVGT_16   = 0b00011000 # defalut
AVGT_32   = 0b00100000
AVGT_64   = 0b00101000
AVGT_128  = 0b00110000
AVGT_256  = 0b00111000

# CTRL_REG1
PD        = 0b10000000 # Power Down control
BDU       = 0b00000100 # Block Data Update control
ODR_ONE   = 0b00000000 # Output Data Rate : One Shot
ODR_1HZ   = 0b00000001 # Output Data Rate : 1Hz
ODR_7HZ   = 0b00000010 # Output Data Rate : 7Hz
ODR_125HZ = 0b00000011 # Output Data Rate : 12.5Hz

# CTRL_REG2
BOOT      = 0b10000000 # Reboot memory content
HEATER    = 0b00000010 # Heater
ONE_SHOT  = 0b00000001 # One shot enable

# CTRL_REG3
CTRL_REG3_DEFAULT = 0x00 # DRDY pin is no connect in FaBo Brick

# STATUS_REG
H_DA           = 0x02 # Humidity Data Available
T_DA           = 0x01 # Temperature Data Available

# Register Addresses
AV_CONF        = 0x10
CTRL_REG1      = 0x20
CTRL_REG2      = 0x21
CTRL_REG3      = 0x22
STATUS_REG     = 0x27
HUMIDITY_OUT_L = 0x28
HUMIDITY_OUT_H = 0x29
TEMP_OUT_L     = 0x2A
TEMP_OUT_H     = 0x2B
H0_RH_X2       = 0x30
H1_RH_X2       = 0x31
T0_DEGC_X8     = 0x32
T1_DEGC_X8     = 0x33
T1_T0_MSB      = 0x35
H0_T0_OUT_L    = 0x36
H0_T0_OUT_H    = 0x37
H1_T0_OUT_L    = 0x3A
H1_T0_OUT_H    = 0x3B
T0_OUT_L       = 0x3C
T0_OUT_H       = 0x3D
T1_OUT_L       = 0x3E
T1_OUT_H       = 0x3F

## smbus
bus = smbus.SMBus(1)

## FaBo Humidity I2C Controll class
class HTS221:

    ## Constructor
    #  @param [in] address HTS221 I2C slave address default:0x5f
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address

        self.powerOn()
        self.configDevice()
        self.readCoef()

    ## デバイス接続確認
    # @retval true 接続中
    # @retval false デバイス無し
    def searchDevice(self):
        who_am_i = bus.read_byte_data(self.address, DEVID_REG)

        if who_am_i == DEVICE_ID:
            return True
        else:
            return False

    ## デバイス起動、データレート設定
    def powerOn(self):
        data = PD | ODR_1HZ
        bus.write_byte_data(self.address, CTRL_REG1, data)

    ## 出力データ解像度設定
    def configDevice(self):
        data = AVGH_32 | AVGT_16
        bus.write_byte_data(self.address, AV_CONF, data)

    ## 校正データの読み込み
    def readCoef(self):

        h0_rh = bus.read_byte_data(self.address, H0_RH_X2)
        h1_rh = bus.read_byte_data(self.address, H1_RH_X2)

        self.h0_rh_x2 = h0_rh #uint8
        self.h1_rh_x2 = h1_rh #uint8

        data = bus.read_byte_data(self.address, T1_T0_MSB)

        t0_degc_x8 = bus.read_byte_data(self.address, T0_DEGC_X8)
        t1_degc_x8 = bus.read_byte_data(self.address, T1_DEGC_X8)
        self.t0_degc_x8 = ((data & 0x3 ) << 8) | t0_degc_x8 #uint16
        self.t1_degc_x8 = ((data & 0xC ) << 6) | t1_degc_x8 #uint16

        h0_t0_l = bus.read_byte_data(self.address, H0_T0_OUT_L)
        h0_t0_h = bus.read_byte_data(self.address, H0_T0_OUT_H)
        self.h0_t0_out  = self.dataConv(h0_t0_l, h0_t0_h) #int16

        h1_t0_l = bus.read_byte_data(self.address, H1_T0_OUT_L)
        h1_t0_h = bus.read_byte_data(self.address, H1_T0_OUT_H)
        self.h1_t0_out  = self.dataConv(h1_t0_l, h1_t0_h) #int16

        t0_l = bus.read_byte_data(self.address, T0_OUT_L)
        t0_h = bus.read_byte_data(self.address, T0_OUT_H)
        self.t0_out  = self.dataConv(t0_l, t0_h) #int16

        t1_l = bus.read_byte_data(self.address, T1_OUT_L)
        t1_h = bus.read_byte_data(self.address, T1_OUT_H)
        self.t1_out  = self.dataConv(t1_l, t1_h) #int16

    ## 湿度出力
    #  @return 湿度(Rh%)
    def readHumi(self):
        humidity = 0.0

        data = bus.read_byte_data(self.address, STATUS_REG)

        if data & H_DA :

            h_out_l = bus.read_byte_data(self.address, HUMIDITY_OUT_L)
            h_out_h = bus.read_byte_data(self.address, HUMIDITY_OUT_H)

            h_out  = self.dataConv(h_out_l, h_out_h)

            # 1/2にする
            t_H0_rH = self.h0_rh_x2 / 2.0
            t_H1_rH = self.h1_rh_x2 / 2.0
            # 線形補間でもとめる
            humidity = t_H0_rH + ( t_H1_rH - t_H0_rH ) * ( h_out - self.h0_t0_out ) / ( self.h1_t0_out - self.h0_t0_out )

        return humidity

    ## 温度出力
    #  @return 温度(Deg C)
    def readTemp(self):
        temperature = 0.0

        data = bus.read_byte_data(self.address, STATUS_REG)

        if data & T_DA :
            temp_out_l = bus.read_byte_data(self.address, TEMP_OUT_L)
            temp_out_h = bus.read_byte_data(self.address, TEMP_OUT_H)
            t_out  = self.dataConv(temp_out_l, temp_out_h) #int16

            # 1/8にする
            t_T0_degC = self.t0_degc_x8 / 8.0
            t_T1_degC = self.t1_degc_x8 / 8.0
            # 線形補間でもとめる
            temperature = t_T0_degC + ( t_T1_degC - t_T0_degC ) * ( t_out - self.t0_out ) / ( self.t1_out - self.t0_out )

        return temperature

    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

if __name__ == "__main__":
    hts221 = HTS221()

    while True:
        humi = hts221.readHumi()
        temp = hts221.readTemp()
        print "Humidity = ", humi
        print "Temp     = ", temp
        print
        time.sleep(1)
