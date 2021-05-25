import os
import time
import json
import datetime
from speedflux.config import get_config
from speedflux.influx import Influx

config = get_config()
influxdb_client = Influx(config)



def pkt_loss(data):
    if 'packetLoss' in data.keys():
        return int(data['packetLoss'])
    else:
        return 0


def main():
    pPing = Process(target=pingtest)
    pSpeed = Process(target=speedtest)

    init_db()  # Setup the database if it does not already exist.

    loopcount = 0
    while (1):  # Run a Speedtest and send the results to influxDB indefinitely.
        if loopcount == 0 or loopcount % PING_INTERVAL == 0:
            if pPing.is_alive():
                pPing.terminate()
            pPing = Process(target=pingtest)
            pPing.start()

        if loopcount == 0 or loopcount % TEST_INTERVAL == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=speedtest)
            pSpeed.start()

        if loopcount % ( PING_INTERVAL * TEST_INTERVAL ) == 0:
            loopcount = 0

        time.sleep(1)
        loopcount += 1

if __name__ == '__main__':
    print('Speedtest CLI data logger to InfluxDB started...')
    main()
