#include "ESP8266WiFi.h"
#define lights_port D3
#define trackers_port D0
#include <Wire.h>                                       
#include <Adafruit_BME280.h>            
#include <Adafruit_Sensor.h>                     
#define SEALEVELPRESSURE_HPA (1013.25)



#define engine1_port D5
#define engine2_port D6
#define engine3_port D7

Adafruit_BME280 bme;          

const char* ssid = "23";
const char* password =  "";

bool lights_are_on = 1;
bool trackers_are_on = 0;

bool engine1_is_on = false;
bool engine2_is_on = false;
bool engine3_is_on = false;

String res = "";

float temperature;
float humidity;
float altitude;
float pressure;

unsigned long previousMillis = 0;        // will store last temp was read
const long interval = 2000;   
WiFiServer wifiServer(80);
WiFiClient client;

String update_data(String key=""){ 
  String to_send = "";
  if (key == "temperature"){
      temperature = (int)bme.readTemperature();
      to_send += "temperature=" + String(temperature) + ";";
    } else if (key == "altitude"){
      altitude = (int)bme.readAltitude(SEALEVELPRESSURE_HPA);
      to_send += "altitude=" + String(altitude) + ";";
    } else if (key == "pressure") {
      pressure = bme.readPressure();
      to_send +=  "pressure=" + String(pressure) + ";";
    } else if (key == "humidity"){
      humidity = bme.readHumidity()/ 100.0F;
      to_send += "humidity=" + String(humidity) + ";";
    } else{
      temperature = (int)bme.readTemperature();
      altitude = (int)bme.readAltitude(SEALEVELPRESSURE_HPA);
      pressure = bme.readPressure();
      humidity = bme.readHumidity()/ 100.0F;
      
      to_send += "temperature=" + String(temperature) + ";";
      to_send += "altitude=" + String(altitude) + ";";
      to_send +=  "pressure=" + String(pressure) + ";";
      to_send += "humidity=" + String(humidity) + ";";
    }
 return to_send;
}
  
void setup() {
  Serial.begin(115200);
  pinMode(trackers_port, OUTPUT);
  pinMode(lights_port, OUTPUT);
  pinMode(engine1_port, OUTPUT);
  pinMode(engine2_port, OUTPUT);
  pinMode(engine3_port, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, LOW);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to ");
  Serial.println(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting..");
  }
  
  if (!bme.begin(0x76)) {                
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);                                  
  }
  
  Serial.print("Connected to WiFi. IP:");
  Serial.println(WiFi.localIP());
  digitalWrite(LED_BUILTIN, HIGH);
  wifiServer.begin();
}


  
String dataString() {
  String res = "";
  if (trackers_are_on) {
    res += "trackers_are_on=on;";
  } else {
    res += "trackers_are_on=off;";
  }

  if (lights_are_on) {
    res += "lights_are_on=on;";
  } else {
    res += "lights_are_on=off;";
  }
  return res;
}

void loop() {
  if (!client.connected()) {
    client = wifiServer.available();
  } else {
    if (client.available() > 0) {
      res += char(client.read());
    } else if (res != "") {
      Serial.println(res);
      if (res != "") {
        Serial.println("{" + res + "}");
        String to_send = "";
        if (res == "enable_light" || res ==  "enable_lights") {
          lights_are_on = true;
          Serial.println("- Enabled lights");

        } else if (res == "disable_light" || res == "disable_lights") {
          lights_are_on = false;
          Serial.println("- Disabled lights");

        } else if (res == "enable_trackers") {
          trackers_are_on = true;
          Serial.println("- Enabled trackers");

        } else if (res == "disable_trackers") {
          trackers_are_on = false;
          Serial.println("- Disabled trackers");
          
        } else if (res == "disable_all") {
          trackers_are_on  = false;
          lights_are_on = false;
          Serial.println("- Disabled everything");
          
        } else if (res == "enable_all") {
          trackers_are_on = true;
          lights_are_on = true;
          Serial.println("- Enabled everything");
          
        } else if (res == "reboot") {
          Serial.begin(115200);
          
        } else if (res == "enable_left_engine"){
          engine1_is_on = true;
        } else if (res == "enable_middle_engine"){
          engine2_is_on = true;
        } else if (res == "enable_right_engine"){
          engine3_is_on = true;
        } else if (res == "disable_left_engine"){
          engine1_is_on = false;
        } else if (res == "disable_middle_engine"){
          engine2_is_on = false;
        } else if (res == "disable_right_engine"){
          engine3_is_on = false;
        }  else if (res == "update_temperature"){
          to_send += update_data("temperature");
          
        } else if (res == "update_altitude"){
          to_send += update_data("altitude");
          
        } else if (res == "update_humidity"){
          to_send += update_data("humidity");
          
        } else if (res == "update_pressure"){
          to_send += update_data("pressure");
          
        } else {
           to_send += update_data();
        }
        Serial.println(engine1_is_on);
        Serial.println(engine2_is_on);
        Serial.println(engine3_is_on);
        client.println(dataString() + to_send);
        res = "";
      }
    }


    if(engine1_is_on){
      digitalWrite(engine1_port, HIGH);
    } else {
      digitalWrite(engine1_port, LOW);
    }

    if(engine2_is_on){
      digitalWrite(engine2_port, HIGH);
    } else {
      digitalWrite(engine2_port, LOW);
    }

    if(engine3_is_on){
      digitalWrite(engine3_port, HIGH);
    } else {
      digitalWrite(engine3_port, LOW);
    }


    if (trackers_are_on) {
      digitalWrite(trackers_port, HIGH);
    } else {
      digitalWrite(trackers_port, LOW);
    }

    if (lights_are_on) {
      digitalWrite(lights_port, HIGH);
    } else {
      digitalWrite(lights_port, LOW);
    }
  }
}
