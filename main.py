import os
import time

from speedflux.config import get_config
from speedflux.influx import Influx
from multiprocessing import Process
from speedflux.data import speedtest, pingtest
from speedflux.logs import log

def main():
    config = get_config()
    influx = Influx(config)
    config['influx'] = influx
    pPing = Process(target=pingtest, args=(config,))
    pSpeed = Process(target=speedtest, args=(config,))

    loopcount = 0
    while (1):  # Run a Speedtest and send the results to influxDB indefinitely.
        if loopcount == 0 or loopcount % config['ping_interval'] == 0:
            if pPing.is_alive():
                pPing.terminate()
            pPing = Process(target=pingtest, args=(config,))
            pPing.start()

        if loopcount == 0 or loopcount % config['test_interval'] == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=speedtest, args=(config,))
            pSpeed.start()

        if loopcount % ( config['ping_interval'] * config['test_interval'] ) == 0:
            loopcount = 0

        time.sleep(1)
        loopcount += 1

if __name__ == '__main__':
    log.info('Speedtest CLI data logger to InfluxDB started...')
    main()
