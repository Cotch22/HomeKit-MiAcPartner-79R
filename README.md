偶然看到这个项目，很惊喜，感谢[@Hcreak](https://github.com/Hcreak)。  

发现大家关于 HomeKit 的 HeaterCooler 类型持放弃态度，基本都把空调转向了 Thermostat 类型，这样失去了很多 HeaterCooler 的特性能力，我觉得得不偿失。  

我尝试了一下 Siri 调温的策略，Siri 调温是基于当前温度 `CurrentTemperature` 来做设定的，但是在不连接外部温度传感器的情况下，如何给定这个值呢。  

很简单！制冷模式下，我们只需要给一个比设定温度高的值就可以获得一个 '正在制冷' 的状态，制热同理，那我们怎么知道空调在制冷呢。  

同样很简单！首先感谢[@Hcreak](https://github.com/Hcreak)的铺路，我们可以通过对空调当前的功率的判断来知晓空调的工作状态。

我这里是 5s 查询一次，如果功率很低，说明压缩机没有在工作，这个时候就可以给 `CurrentHeaterCoolerState` 一个值 `1` 实现 HomeKit 中空调状态显示为 '闲置'，并将 `CurrentTemperature` 设置为和设定温度一样，此时用 Siri 调温就是以当前设定温度为基础调温。  
如果功率很高，说明压缩机在工作，HomeKit 中空调状态就会显示为 '正调低至' 或 '正调高至'，此时 Siri 会用很聪明的方式回答你的调温请求，自己试试吧！  

只留下了核心内容，去掉了 web 和 sql 部分，意在提供思路。  

目前自动模式没有做特殊修改，因为 HomeKit 空调的自动模式会同时使用 `CoolingThresholdTemperature` 与 `HeatingThresholdTemperature` 两个设定值，目前没有想出用户友好的解决方案，建议不用自动模式。

由于 HomeKit 没有自动风速选项，我的解决方案是滑条滑到最左也就是风速值为 0 时，会给空调伴侣发送自动风速指令，同时，在下一个 5s 后，会返回一个当前风速现实到滑条上。

---

# HomeKit-MiAcPartnerMcn02

专用于丐版粗粮空调伴侣2（lumi.acpartner.mcn02） 接入HomeKit

**为了正常使用Siri调节温度 这里使用Thermostat 牺牲掉了使用频率不高的风量调节和扫风开关 若必须这两个功能 请切换到停止维护的HeaterCooler分支**

## Require
  * [HAP-python[QRCode]](https://github.com/ikalchev/HAP-python)
  * [python-miio](https://github.com/rytilahti/python-miio)

## Usage

```bash
    export MCN02_IP= 空调伴侣IP
    export MCN02_TOKEN= 空调伴侣Token
    python3 main.py
```

## Deploy

**Docker部署目前仅适配ARM32v7架构**

```bash
    docker build -t hap_mcn02 .
    docker run -d --network host --name myhap_mcn02 -e MCN02_IP= 空调伴侣IP -e MCN02_TOKEN= 空调伴侣Token hap_mcn02
```

### macvlan network 部署
```bash
    docker network create -d macvlan   --subnet=10.10.10.0/24   --gateway=10.10.10.1  --ip-range=10.10.10.200/29  -o parent=eth0 mvc0
    docker run -d --network mvc0 --name myhap_mcn02 -e MCN02_IP= 空调伴侣IP -e MCN02_TOKEN= 空调伴侣Token hap_mcn02
```


## Notice

1. 需自行获取空调伴侣的IP和Token

    * 一种方法是使用毛子修改版米家APP：

        https://www.kapiba.ru/2017/11/mi-home.html

2. 粗粮坑爹 空调伴侣没有温度传感器 ~~而 `HomeKit` 规定 `HeaterCooler Service` 的`CurrentTemperature` 为必选参数 因此这里只能把目标温度作为当前温度传入 实际使用中发现这样做在使用Siri时可能有Bug 以后会考虑提供接口从外部的温度传感器引入环境温度~~ 

   * **已将 Service 类型改为 Thermostat 以解决使用Siri调节温度模式错乱的问题**
     
     问题的原因在于Siri语音逻辑的更改 与之前推测的当前温度数值无关

     * https://github.com/homebridge/HAP-NodeJS/issues/577

     * https://github.com/wailuen/homebridge-sensibo-sky/issues/26

3. 还是粗粮坑爹 尽管 `miio` 协议为内网通讯 但实测发现 若给空调伴侣切断外网 则发送指令正常返回但不动作 目前抓包并没有发现空调伴侣对内网扫描的情况发生 至于用不用各位自己掂量吧

4. 还还还是粗粮坑爹 在对米家APP与空调伴侣通讯的 `miio` 协议抓包解析过程中 并没有发现用电量统计的数据字段 推测应该是空调伴侣上报用电量到粗粮服务器上 APP从服务器获取用电量数据 空调伴侣本身不对用电量进行存储 ~~这样的话就没办法用 `miio` 协议去获取用电量数据来展示了~~ 

   * **加入电量统计功能 每分钟读取一次负载功率 计算成电量值后累加 存入数据库**
     
   * **5000端口开启web可视化展示 点击数据点可查看具体每天耗电量及原始采集功率数据**
