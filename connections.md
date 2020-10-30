# Connections
The connections that is used in the display following [this pinout](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/wiring.md).

### Hub75 Pinout
Below is the pinout of the hub75 connector.
This is the female header as seen from the bottom.

(green and blue are switched here, because it is an RBG screen)

|--->|--->|
|-|-|
|B1|R1|
|GND|G1|
|B2|R2|
|GND|G2|
|B|A|
|D|C|
|STROBE|CLK|
|GND|OE-|

### Pi Pinout
Below is how it should be connected to the pi.
This is the male header as seen from the top of the pi.

|symbol|meaning|
|-|-|
|(1)|connected to chain 1|
|(2)|connected to chain 2|
|(*)|connected to all chains|

|Connection|Pin|Pin|Connection|
|-|-|-|-|
|-|1|2|5V+|
|-|3|4|-|
|-|5|6|(*) GND|
|(*) STROBE|7|8|-|
|(*) GND|9|10|-|
|(*) CLK|11|12|(*) OE-|
|(1) G1|13|14|(*) GND|
|(*) A|15|16|(*) B|
|-|17|18|(*) C|
|(1) B2|19|20|(*) GND|
|(1) G2|21|22|-|
|(1) R1|23|24|(1) R2|
|(*) GND|25|26|(1) B1|
|-|27|28|-|
|(2) G1|29|30|(*) GND|
|(2) B1|31|32|(2) R1|
|(2) G2|33|34|(*) GND|
|(2) R2|35|36|-|
|-|37|38|(2) B2|
|(*) GND|39|40|-|
