import time

import speedflux
from multiprocessing import Process


def main():
    speedflux.initialize()
    pPing = Process(target=speedflux.data.pingtest, args=())
    pSpeed = Process(target=speedflux.data.speedtest, args=())

    loopcount = 0
    while (1):  # Run a Speedtest and send the results to influxDB
        if loopcount == 0 or loopcount % speedflux.CONFIG.PING_INTERVAL == 0:
            if pPing.is_alive():
                pPing.terminate()
            pPing = Process(target=speedflux.data.pingtest, args=())
            pPing.start()

        if loopcount == 0 or loopcount % speedflux.CONFIG.TEST_INTERVAL == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=speedflux.data.speedtest, args=())
            pSpeed.start()

        if loopcount % (speedflux.CONFIG.PING_INTERVAL *
                        speedflux.CONFIG.TEST_INTERVAL) == 0:
            loopcount = 0

        time.sleep(1)
        loopcount += 1


if __name__ == '__main__':
    speedflux.LOG.info('Speedtest CLI data logger to InfluxDB started...')
    main()
