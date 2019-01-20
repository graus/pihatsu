import datetime
import time
import obd

obd.logger.setLevel(obd.logging.DEBUG)

def connect_obd():
    while True:
        conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=None, fast=False)
        if conn.is_connected():
            obd.logger.debug("Connected! Returning {}".format(conn))
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
            data = [get_timestamp()] + [c.value for c in data]

            csv_file.write("\t".join(map(str, data)) + "\n")
            csv_file.flush()

        obd.logger.debug("Disconnected(?) Reconnecting + restarting main...")

        conn = connect_obd()
        main(conn, commands)



if __name__ == "__main__":
    conn = connect_obd()

    cmds = {b'0103', b'0104', b'0105', b'0106', b'0107', b'010B', b'010C', b'010D', b'010E', b'010F', b'0111', b'0113',
            b'0114', b'0115'}  # extracted from logs
    cmds = [c for c in obd.commands[1] if c.command in cmds]

    force_push_commands(conn, '/home/graus/obd-all-commands.tsv')
    main(conn, cmds)
