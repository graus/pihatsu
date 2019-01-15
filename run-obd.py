import sys
import datetime
import obd

obd.logger.setLevel(obd.logging.DEBUG)

def get_time():
	return datetime.datetime.now().replace(microsecond=0).isoformat()

conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=None, fast=False)  # TODO: reconnect if connection fails
if not conn.is_connected():
	sys.exit(1)

cmds = {b'0103', b'0104', b'0105', b'0106', b'0107', b'010B', b'010C', b'010D', b'010E', b'010F', b'0111', b'0113',
        b'0114', b'0115'}  # extracted from logs
commands = [c for c in obd.commands[1] if c.command in cmds]
header = ["time"] + [c.name for c in commands]

with open('/home/graus/{}.csv'.format(get_time()), 'a') as csv_file:
	csv_file.write("\t".join(header) + "\n")

	while conn.is_connected():  # TODO: replace with something smarter/cleaner
		data = [conn.query(c) for c in commands]
		data = [get_time()] + [c.value.magnitude for c in data]

		csv_file.write("\t".join(map(str, data)) + "\n")
		csv_file.flush()
