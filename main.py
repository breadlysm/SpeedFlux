import time

import speedflux
from multiprocessing import Process
from speedflux import data


def main():
    speedflux.initialize()
    speedflux.LOG.info('Speedtest CLI data logger to InfluxDB started...')
    pPing = Process(target=data.pingtest, args=())
    pSpeed = Process(target=data.speedtest, args=())
    speedtest_interval = speedflux.CONFIG.SPEEDTEST_INTERVAL * 60
    ping_interval = speedflux.CONFIG.PING_INTERVAL
    loopcount = 0
    while (1):  # Run a Speedtest and send the results to influxDB
        if ping_interval != 0:
            if loopcount == 0 or loopcount % ping_interval == 0:
                if pPing.is_alive():
                    pPing.terminate()
                pPing = Process(target=data.pingtest, args=())
                pPing.start()

        if loopcount == 0 or loopcount % speedtest_interval == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=data.speedtest, args=())
            pSpeed.start()
        if ping_interval != 0:
            if loopcount % (ping_interval * speedtest_interval) == 0:
                loopcount = 0
        else:
            if loopcount == speedtest_interval:
                loopcount = 0
        time.sleep(1)
        loopcount += 1


if __name__ == '__main__':
    main()
