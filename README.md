# homeassistant-yunmi

把所有代码放在 `custom_components/yunmi` 目录中，在 configuration.yaml 中做相应配置：

## 饮水吧

* 已测试版本：`yunmi.kettle.r1`

```
water_heater:
  - platform: yunmi
    host: xxx.xxx.xxx.xxx
    token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    name: Yunmi Kettle
```

通过 template sensor 查看水质 tds

```
sensor:
  - platform: template
    sensors:
      kettle_tds:
        friendly_name: "Kettle TDS"
        value_template: "{{ state_attr('water_heater.yunmi_kettle', 'tds') }}"
        icon_template: "mdi:cup-water"
        unit_of_measurement: 'ppm'
```

## 油烟机

* 已测试版本：`viomi.hood.c1`

```
fan:
  - platform: yunmi
    name: Yunmi Hood
    host: xxx.xxx.xxx.xxx
    token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 ```
 
 通过 service 控制油烟机灯光：
 
 ```
 yunmi.set_light_on
 yunmi.set_light_off
 ```

## 鸣谢

饮水吧协议参考了 lukezzz 的 [homeassistant-yunmi-kettle](https://github.com/lukezzz/homeassistant-yunmi-kettle) ，将多个 sensor 改造为 water_heater 组件
