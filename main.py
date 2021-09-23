import logging
import signal

from miio_wrapper import *

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_AIR_CONDITIONER

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class XiaoMiAcPartnerMcn02(Accessory):
    category = CATEGORY_AIR_CONDITIONER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            value=miio_get_power(),
            setter_callback=self._on_active_changed
        )

        self.char_curmode = serv_HC.configure_char('CurrentHeaterCoolerState', value=0)

        self.char_tarmode = serv_HC.configure_char(
            'TargetHeaterCoolerState',
            value=miio_get_mode(),
            valid_values={"Auto": 0, "Cool": 2, "Heat": 1},
            setter_callback=self._on_tarmode_changed
        )

        self.char_curtemp = serv_HC.configure_char('CurrentTemperature')

        self.char_tartempC = serv_HC.configure_char(
            'CoolingThresholdTemperature',
            setter_callback=self._on_tartempC_changed
        )

        self.char_tartempH = serv_HC.configure_char(
            'HeatingThresholdTemperature',
            setter_callback=self._on_tartempH_changed
        )

        self.char_swing = serv_HC.configure_char(
            'SwingMode',
            value=miio_get_swing(),
            setter_callback=self._on_swing_changed
        )

        self.char_fanspeed = serv_HC.configure_char(
            'RotationSpeed',
            value=miio_get_fanspeed(),
            setter_callback=self._on_fanspeed_changed
        )

        mode = miio_get_mode()
        if mode == 0 or mode == 2:
            self.char_tartempC.set_value(miio_get_temp())
            self.char_tartempH.set_value(35)
        elif mode == 1:
            self.char_tartempH.set_value(miio_get_temp())
            self.char_tartempC.set_value(10)

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
        miio_set_mode(value)
        if value == 0 or value == 2:
            self.char_tartempC.set_value(miio_get_temp())
            self.char_tartempH.set_value(35)
        elif value == 1:
            self.char_tartempH.set_value(miio_get_temp())
            self.char_tartempC.set_value(10)
        print('TargetHeaterCoolerState {}'.format(value))

    @Accessory.run_at_interval(5)
    async def run(self):
        temp = miio_get_temp()
        if miio_get_load() < 300:
            self.char_curmode.set_value(1)
            self.char_curtemp.set_value(temp)
        else:
            mode = miio_get_mode()
            self.char_curmode.set_value(mode + 1)
            if mode == 2:
                self.char_tartempC.set_value(temp)
                self.char_curtemp.set_value(temp + 1)
            elif mode == 1:
                self.char_tartempH.set_value(temp)
                self.char_curtemp.set_value(temp - 1)
        self.char_fanspeed.set_value(miio_get_fanspeed())
        self.char_swing.set_value(miio_get_swing())
        self.char_active.set_value(miio_get_power())


def get_accessory(driver):
    return XiaoMiAcPartnerMcn02(driver, '米家空调伴侣2')


if __name__ == '__main__':
    driver = AccessoryDriver(port=51826)
    driver.add_accessory(accessory=get_accessory(driver))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()
