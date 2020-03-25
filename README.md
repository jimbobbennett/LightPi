# LightPi

A general purpose Azure IoT Central powered light control system for Raspberry Pis.

## Aims

The aim of this project is to provide a generic application that can be installed on a Raspberry Pi running Raspbian to control lights using Azure IoT Central.

The project will consist of:

* An install script that installs the code on the Pi, including any libraries for lights, then configures it to connect to an IoT Central app
* The software to control various lights including the [Pimoroni Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat), [Pimoroni Blinkt](https://shop.pimoroni.com/products/blinkt), [NeoPixel strips](https://www.adafruit.com/product/1138?length=1), and [WS2812 LED strips](https://www.amazon.com/gp/product/B07FVPN3PH/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1).

The control software will connect to Azure IoT Central using a pre-defined application template. It will be sent color requests as IoT Central commands. These requests will be in one of a few formats:

* Single color values - all the LEDs/pixels will change to this color
* An array of color values - the colors in this array will be applied to the LEDs/pixels in order, repeating if there are more LEDs/pixels than array elements
* Time offsets and single colors - a timer loop will work through these colors, lighting all the LEDs/pixels in each color, then waiting the time offset to apply the new color
* Time offsets and arrays of color values - a timer loop will work through these colors, lighting all the LEDs/pixels using the color array, then waiting the time offset to apply the new color

## Supported lights

The first version will support these lights:

* [Pimoroni Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat)
* [Pimoroni Blinkt](https://shop.pimoroni.com/products/blinkt)
* [NeoPixel strips](https://www.adafruit.com/product/1138?length=1)
* [WS2812 LED strips](https://www.amazon.com/gp/product/B07FVPN3PH/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1)

Instructions for connecting the lights will be in the [`hardware-instructions` folder](./hardware-instructions).