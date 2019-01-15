import sys
import datetime
import obd

obd.logger.setLevel(obd.logging.DEBUG)

conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=None, fast=False)

with open('/home/graus/all-commands.csv', 'a') as csv_file:
    for c in obd.commands[1]:
        r = conn.query(c, force=True)
        csv_file.write("{}:{}\n".format(c.name, str(r.value)))
        csv_file.flush()

conn.close()

