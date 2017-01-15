#import RPi.GPIO as GPIO
from time import sleep
#from RPi.GPIO import output as output

pin = 21
signal = '11000100 11010011 01100100 10000000 00000000 00000100 00010000 10010000 00001100 10000010 00000000 00000000 00000000 00000000 00000000 00000000 00000000 11101101'

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)


def send():

    total = 0

    #output(pin, 1)
    sleep(0.003470)
    print(('%d' % (3470,)).rjust(8)),
    total += 3470

    #output(pin, 0)
    sleep(0.001650)
    print(('%d' % (1650,)).rjust(8)),
    total += 1650

    added = 2

    for i in signal:

        if i == ' ':
            continue

        #output(pin, 1)
        sleep(0.000480)
        print(('%d' % (480,)).rjust(8)),
        total += 480

        #output(pin, 0)
        if i == '1':
            sleep(0.001230)
            print(('%d' % (1230,)).rjust(8)),
            total += 1230

        else:
            sleep(0.000380)
            print(('%d' % (380,)).rjust(8)),
            total += 380

        added += 2
        if added % 6 == 0:

            print('')

    #output(pin, 1)
    sleep(0.000450)
    print(('%d' % (450,)).rjust(8)),
    total += 450

    #output(pin, 0)
    sleep(0.013250)
    print(('%d' % (13250,)).rjust(8)),
    total += 13250

    print('\n\n\n\n' + str(total))

send()
