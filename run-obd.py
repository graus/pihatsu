import datetime
import time
import obd
from serial import SerialException

obd.logger.setLevel(obd.logging.DEBUG)


def connect_obd():
    """
    Establish connection w/ OBD2 with 10 sec re-try intervals
    """

    while True:
        try:
            conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=None, fast=False)
        except SerialException:
            time.sleep(10)
            continue

        if conn.is_connected():
            return conn

        else:
            obd.logger.debug("Unable to connect, trying again in 10...")
            time.sleep(10)


def get_timestamp():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def force_push_commands(conn, output_file):
    """
    Force push all commands (in mode 1).
    """

    with open(output_file, 'a') as out_file:  # TODO: one-time force query to check supported commands
        for c in obd.commands[1]:
            r = conn.query(c, force=True)
            out_file.write("{}\t{}\n".format(c.name, str(r.value)))
            out_file.flush()


def main(conn, commands):
    """
    Main loop that keeps querying OBD while connected, and reconnects when disconnected (?)
    """

    header = ["time"] + [c.name for c in commands]
    filename = '/home/graus/data/{}.tsv'.format(get_timestamp())

    with open(filename, 'a') as csv_file:
        csv_file.write("\t".join(header) + "\n")

        while conn.is_connected():
            data = [conn.query(c) for c in commands]
            data = [get_timestamp()] + [c.value for c in data]  # TODO: write raw values (magnitude?)

            csv_file.write("\t".join(map(str, data)) + "\n")
            csv_file.flush()

        obd.logger("Lost connection?")


if __name__ == "__main__":
    cmds = ['RPM', 'SPEED', 'ENGINE_LOAD', 'COOLANT_TEMP', 'FUEL_STATUS', 'SHORT_FUEL_TRIM_1', 'LONG_FUEL_TRIM_1',
            'INTAKE_PRESSURE', 'TIMING_ADVANCE', 'INTAKE_TEMP', 'THROTTLE_POS', 'O2_B1S1', 'O2_B1S2']
    cmds = [c for c in obd.commands[1] if c.name in cmds]

    while True:
        conn = connect_obd()
        main(conn, cmds)
