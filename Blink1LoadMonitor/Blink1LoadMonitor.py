#!/usr/bin/python3 -u

import math
import signal
import sys
import logging
import traceback
import time
import psutil
from blink1.blink1 import Blink1

def setMyPattern(myBlink):
    targetPattern = [(255, 0, 0, 500), (255, 0, 0, 500), (0, 0, 0, 500), (0, 0, 0, 500), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100), (0, 0, 0, 100)]
    if targetPattern != myBlink.read_pattern():
        myBlink.write_pattern_line(500, 'red', 0, 1)
        myBlink.write_pattern_line(500, 'red', 1, 2)
        myBlink.write_pattern_line(500, 'black', 2, 1)
        myBlink.write_pattern_line(500, 'black', 3, 2)
        for iLine in range(4,16):
            myBlink.write_pattern_line(100, 'black', iLine, 0)
        myBlink.save_pattern()


"""return value constrained to 0...255"""
def constrainByte(value):
    if (value < 0):
        logging.warning(traceback.format_stack() + "  constraining value from " + str(value), " to 0\n")
        return 0
    elif (value > 255):
        logging.warning(traceback.format_stack() + "  constraining value from " + str(value), " to 255\n")
        return 255
    else:
        return value

"""map 0...100 to 0...255"""
def perc2byte(perc):
    return constrainByte(perc * 255 / 100)

"""map transfer rate to 0...255"""
def trans2byte(trans):
    if trans < 0.0:
        return 0
    else:
        return constrainByte(math.pow(trans,0.27))

"""translate the interval in seconds to fade time in milliseconds"""
def interval2fadeMS(interval):
    return interval*1.0*1000.0


def main():
    """configuration values"""
    freq = 4.0
    interval = 1.0/freq
    run = True
    blink1Id = ''
    blink1Found = False
    cliOutput = False
    display = False
    multiLed = False

    logging.basicConfig(filename='Blink1LoadMonitor.log',
                        encoding='utf-8',
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    """activating CLI output if specified"""
    for argument in sys.argv:
        if argument == "-v" or argument == "--verbose":
            cliOutput = True
            print("activating CLI output")
            logging.info("activating CLI output")
        elif argument == "-d" or argument == "--display":
            display = True
            print("activating data output to CLI")
            logging.info("activating data output to CLI")
        elif argument == "-m" or argument == "--multiLed":
            multiLed = True
            print("activating output on extra LEDs")
            logging.info("activating output on extra LEDs")
        elif argument[0:2] == "-d":
            blink1Id = argument[2:]


    while run:
        """get Blink1 device handle"""
        try:
            if blink1Id == '':
                b1 = Blink1()
            else:
                b1 = Blink1(blink1Id)
            logging.info("blink1({}) found".format(b1.get_serial_number()))
            if cliOutput:
                print("blink1({}) found".format(b1.get_serial_number()))
            blink1Found = True

            """init """
            setMyPattern(b1)
            nextRun = time.time() + interval
            disk_io_old = psutil.disk_io_counters()
            net_io_old = psutil.net_io_counters()

            b1.fade_to_rgb(0, 0, 0, 0, 0)
        except Exception as e:
            blink1Found = False
            logging.info(str(e))
            time.sleep(interval)

        """run main loop"""
        while blink1Found:
            now = time.time()
            if now < nextRun:
                time.sleep(nextRun-now)
            else:
                try:
                    nextRun+=interval

                    """capture data"""
                    cpu = psutil.cpu_percent()
                    bCpu = perc2byte(cpu)

                    mem = psutil.virtual_memory().percent
                    bMem = perc2byte(mem)

                    disk_io = psutil.disk_io_counters(nowrap=True)
                    diskRd = (disk_io.read_bytes-disk_io_old.read_bytes)*freq
                    bDiskRd = trans2byte(diskRd)
                    diskWr = (disk_io.write_bytes-disk_io_old.write_bytes)*freq
                    bDiskWr = trans2byte(diskWr)
                    disk_io_old = disk_io

                    net_io = psutil.net_io_counters(nowrap=True)
                    netRx = (net_io.bytes_recv-net_io_old.bytes_recv)*freq
                    bNetRx = trans2byte(netRx)
                    netTx = (net_io.bytes_sent-net_io_old.bytes_sent)*freq
                    bNetTx = trans2byte(netTx)
                    net_io_old = net_io

                    """livetick for the Blink1"""
                    b1.server_tickle(enable=True, timeout_millis=interval*5.0*1000.0, stay_lit=True)

                    """set Blink1 colors"""
                    b1.fade_to_rgb(interval2fadeMS(interval), bNetTx, bNetRx, bCpu, 1)
                    b1.fade_to_rgb(interval2fadeMS(interval), bDiskWr, bDiskRd, bMem, 2)
                    if multiLed:
                        b1.fade_to_rgb(interval2fadeMS(interval), 0, 0, bCpu, 3)
                        b1.fade_to_rgb(interval2fadeMS(interval), 0, bNetRx, 0, 4)
                        b1.fade_to_rgb(interval2fadeMS(interval), bNetTx, 0, 0, 5)
                        b1.fade_to_rgb(interval2fadeMS(interval), 0, 0, bMem, 6)
                        b1.fade_to_rgb(interval2fadeMS(interval), 0, bDiskRd, 0, 7)
                        b1.fade_to_rgb(interval2fadeMS(interval), bDiskWr, 0, 0, 8)

                    """data output for debugging"""
                    if display:
                        print("\033c", end="")
                        print('mem\t=', mem, '% ', end='\t\t')
                        print('(', round(bMem), ')', sep='')
                        print('cpu\t=', cpu, '% ', end='\t\t')
                        print('(', round(bCpu), ')', sep='')
                        print('diskRd\t=', round(diskRd/1000/1000, 6), 'MB/s', end='\t\t')
                        print('(', round(bDiskRd), ')', sep='')
                        print('diskWr\t=', round(diskWr/1000/1000, 6), 'MB/s', end='\t\t')
                        print('(', round(bDiskWr), ')', sep='')
                        print('netRx\t=', round(netRx/1000/1000, 6), 'MB/s', end='\t\t')
                        print('(', round(bNetRx), ')', sep='')
                        print('netTx\t=', round(netTx/1000/1000, 6), 'MB/s', end='\t\t')
                        print('(', round(bNetTx), ')', sep='')
                    
                    b1.get_version()

                except:
                    if cliOutput:
                        print("blink1 vanished", file=sys.stderr)
                    logging.info("blink1 vanished")
                    b1.close()
                    blink1Found = False

if __name__ == '__main__':
    main()
