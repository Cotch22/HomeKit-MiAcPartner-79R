import miio
import os

target = miio.airconditioningcompanionMCN.AirConditioningCompanionMcn02(
    ip=os.environ.get('MCN02_IP'),
    token=os.environ.get('MCN02_TOKEN'),
    debug=1,
    model='lumi.acpartner.mcn02'
)


def miio_get_statu():
    return target.status()


def miio_get_temp():
    return target.raw_command("get_prop", ["tar_temp"])[0]


def miio_set_temp(tempvalue):
    target.raw_command("set_tar_temp", [int(tempvalue)])


def miio_get_power():
    if target.raw_command("get_prop", ["power"])[0] == "on":
        return 1
    else:
        return 0


def miio_set_power(active):
    if active:
        target.on()
    else:
        target.off()


def miio_get_mode():
    result = target.raw_command("get_prop", ["mode"])[0]
    if result == "cool":
        return 2
    if result == "heat":
        return 1


def miio_set_mode(number):
    if number == 2:
        target.raw_command("set_mode", ["cool"])
    if number == 1:
        target.raw_command("set_mode", ["heat"])


def miio_get_fanspeed():
    result = target.raw_command("get_prop", ["fan_level"])[0]
    if result == "auto_fan":
        return 0
    elif result == "large_fan":
        return 100
    elif result == "medium_fan":
        return 66
    elif result == "small_fan":
        return 33


def miio_set_fanspeed(number):
    if number == 100:
        target.raw_command("set_fan_level", ["large_fan"])
    elif number >= 50:
        target.raw_command("set_fan_level", ["medium_fan"])
    elif number < 50:
        target.raw_command("set_fan_level", ["small_fan"])
    elif number == 0:
        target.raw_command("set_fan_level", ["auto_fan"])


def miio_get_swing():
    if target.raw_command("get_prop", ["ver_swing"])[0] == "on":
        return 1
    else:
        return 0


def miio_set_swing(active):
    if active:
        target.raw_command("set_ver_swing", ["on"])
    else:
        target.raw_command("set_ver_swing", ["off"])


def miio_get_load():
    return target.raw_command("get_prop", ["load_power"])[0]
