# homeassistant-yunmi

## 饮水吧

* 已测试版本：`yunmi.kettle.r1`

```
water_heater:
  - platform: yunmi
    host: xxx.xxx.xxx.xxx
    token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    name: Yunmi Kettle
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
