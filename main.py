"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal

from miio_test import *

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap.const import CATEGORY_AIR_CONDITIONER

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class XiaoMiAcPartnerMcn02(Accessory):
    """Fake Temperature sensor, measuring every 3 seconds."""

    category = CATEGORY_AIR_CONDITIONER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # serv_active = self.add_preload_service('Switch')
        # serv_active.configure_char(
        #     'On', value=False,
        #     setter_callback=self._on_active_changed
        # )

        # serv_temp = self.add_preload_service('TemperatureSensor')
        # self.char_temp = serv_temp.configure_char('CurrentTemperature')

        serv_HC = self.add_preload_service(
            'HeaterCooler', ["Active",
                             "CurrentHeaterCoolerState",
                             "TargetHeaterCoolerState",
                             "CurrentTemperature",
                             "SwingMode",
                             "CoolingThresholdTemperature",
                             "HeatingThresholdTemperature",
                             "RotationSpeed"]
        )

        self.char_active = serv_HC.configure_char(
            'Active',
            setter_callback=self._on_active_changed
        )

        self.char_curmode = serv_HC.configure_char('CurrentHeaterCoolerState')

        self.char_tarmode = serv_HC.configure_char(
            'TargetHeaterCoolerState',
            setter_callback=self._on_tarmode_changed
        )

        self.char_curtemp = serv_HC.configure_char('CurrentTemperature')

        self.char_swing = serv_HC.configure_char(
            'SwingMode',
            setter_callback=self._on_swing_changed
        )

        self.char_tartempC = serv_HC.configure_char(
            'CoolingThresholdTemperature',
            setter_callback=self._on_tartempC_changed
        )

        self.char_tartempH = serv_HC.configure_char(
            'HeatingThresholdTemperature',
            setter_callback=self._on_tartempH_changed
        )

        self.char_fanspeed = serv_HC.configure_char(
            'RotationSpeed',
            setter_callback=self._on_fanspeed_changed
        )


        self.char_active.set_value(miio_get_power())
        mode = miio_get_mode()
        self.char_curmode.set_value(mode)
        if mode == 3:
            self.char_tarmode.set_value(2)
            self.char_tartempC.set_value(miio_get_temp())
            self.char_tartempH.set_value(18)
        else:
            if mode == 2:
                self.char_tarmode.set_value(1)
                self.char_tartempH.set_value(miio_get_temp())
                self.char_tartempC.set_value(24)
            else:
                self.char_tartempC.set_value(24)
                self.char_tartempH.set_value(18)
        self.char_curtemp.set_value(miio_get_temp())
        self.char_swing.set_value(miio_get_swing())
        self.char_fanspeed.set_value(miio_get_fanspeed())


    def _on_active_changed(self, value):
        if miio_get_power() != value:
            miio_set_power(value)
            print('Turn %s' % ('on' if value else 'off'))

    def _on_tartempC_changed(self, value):
        if self.char_tarmode.get_value() == 2:
            miio_set_temp(value)
            print('CoolingThresholdTemperature {}'.format(value))

    def _on_tartempH_changed(self, value):
        if self.char_tarmode.get_value() == 1:
            miio_set_temp(value)
            print('HeatingThresholdTemperature {}'.format(value))

    def _on_fanspeed_changed(self, value):
        miio_set_fanspeed(value)
        print('RotationSpeed {}'.format(value))

    def _on_swing_changed(self, value):
        miio_set_swing(value)
        print('SwingMode {}'.format(value))

    def _on_tarmode_changed(self, value):
        mode = miio_get_mode()
        if value != 0:
            if value == 2 and mode == 3:
                return
            if value == 1 and mode == 2:
                return
            miio_set_mode(value)
            print('TargetHeaterCoolerState {}'.format(value))


    @Accessory.run_at_interval(10)
    async def run(self):
        self.char_curtemp.set_value(miio_get_temp())


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return XiaoMiAcPartnerMcn02(driver, 'MyAcPartner')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_accessory(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()