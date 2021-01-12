#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266HTTPClient.h>

String unique_key = "XtVT7Fy8jQ";

void setup () {

  Serial.begin(115200);
  WiFi.begin("sweet home", "05051979");

  while (WiFi.status() != WL_CONNECTED) {

    delay(1000);
    Serial.println("Connecting..");

  }
  Serial.println("Connected to WiFi Network");

}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://192.168.1.3:8090/ping?key=" + unique_key);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, payload);
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
      } else {
        const char* title = doc["title"];
        Serial.println(title);
        }
    } else {
      Serial.println("An error ocurred");
    }
    http.end();
  }
  delay(1000);
}
