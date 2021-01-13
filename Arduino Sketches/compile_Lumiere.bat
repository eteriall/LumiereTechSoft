Pushd LumiereTechSoft\Arduino Sketches
arduino-cli compile -b esp8266:esp8266:nodemcuv2 %1
arduino-cli upload -p COM5 -b esp8266:esp8266:nodemcuv2 %1
