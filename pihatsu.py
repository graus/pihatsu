import datetime
import time
import obd
from serial import SerialException

obd.logger.setLevel(obd.logging.DEBUG)

cmds = ['RPM',  # revolutions_per_minute
        'SPEED',  # kph
        'THROTTLE_POS', 'ENGINE_LOAD', 'SHORT_FUEL_TRIM_1', 'LONG_FUEL_TRIM_1',  # percent
        'COOLANT_TEMP', 'INTAKE_TEMP',  # degreeC
        'FUEL_STATUS',  # str
        'INTAKE_PRESSURE',  # kilopascal
        'TIMING_ADVANCE',  # degree
        'O2_B1S1', 'O2_B1S2'  # volt
        ]  # handpicked after running `force_push_commands`


def connect_obd():
    """
    Establish connection w/ OBD2 with 10 sec re-try intervals
    """

    obd.logger.debug("Attempting to connect...")

    while True:
        try:
            conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=None, fast=False)
        except SerialException as e:
            obd.logger.debug("SerialException: {}".format(e))
            time.sleep(10)
            continue  # restarts loop

        if conn.is_connected():
            return conn
        else:
            obd.logger.debug("Cannot connect... Retrying in 10")
            time.sleep(10)


def get_timestamp():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def force_push_commands(conn, output_file):
    """
    Force push all commands (in mode 1).
    """

    with open(output_file, 'a') as out_file:
        for c in obd.commands[1]:
            r = conn.query(c, force=True)
            out_file.write("{}\t{}\n".format(c.name, str(r.value)))
            out_file.flush()


def label_session(conn):
    """
    TODO: Script to fetch the label (y) for the data generated in main, i.e., the MAC address of a device that is not
    the radio or OBDII reader (and hopefully someones phone...).
    """

    return None


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
            data = [get_timestamp()] + [c.value for c in data]  # TODO: get raw values (magnitude?)

            csv_file.write("\t".join(map(str, data)) + "\n")
            csv_file.flush()

        obd.logger.debug("Lost connection?")


if __name__ == "__main__":
    cmds = [c for c in obd.commands[1] if c.name in cmds]

    while True:
        conn = connect_obd()
        main(conn, cmds)
