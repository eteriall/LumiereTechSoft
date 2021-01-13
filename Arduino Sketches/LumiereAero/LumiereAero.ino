#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

String unique_key = "XtVT7Fy8jQ";
String HOST = "http://192.168.1.3:8090";
bool CONNECTED_TO_SERVER = false;

void setup () {

  Serial.begin(115200);
  WiFi.begin("sweet home", "05051979");

  while (WiFi.status() != WL_CONNECTED) {

    delay(1000);
    Serial.println("Connecting..");

  }
  Serial.println("Connected to WiFi Network");

}

void log_message(String message){
    HTTPClient report_error_http;
    report_error_http.begin(HOST + "/log_message?message=" + WiFi.macAddress() + "_" + message);
    int report_error_httpCode = report_error_http.GET();
}

void connect(){
    while(!CONNECTED_TO_SERVER){
        if (WiFi.status() == WL_CONNECTED) {

            // Отправляем распределяющему серверу наш MAC - адрес
            HTTPClient http;
            http.begin(HOST + "/connect?mac_address=" + WiFi.macAddress());
            int httpCode = http.GET();

            if (httpCode > 0) {
              /* Получаем обратное сообщение в формате JSON */
              String payload = http.getString();

              DynamicJsonDocument doc(1024);
              DeserializationError error = deserializeJson(doc, payload);

              // Если беда с десериализацией - кидаем сообщение об ошибке
              if (error) {
                Serial.print(F("deserializeJson() failed: "));
                Serial.println(error.f_str());
                HTTPClient report_error_http;
                report_error_http.begin(HOST + "/report?message=" + WiFi.macAddress() + "_Could_not_connect_to_master_page");
                int report_error_httpCode = report_error_http.GET();
              } else {
                // Тут происходит коннект
                String http_code = doc["code"];


                if (http_code != "200"){
                    HTTPClient report_error_http;
                    report_error_http.begin(HOST + "/report?message=" + WiFi.macAddress() + "_Could_not_connect_to_master_page");
                    int report_error_httpCode = report_error_http.GET();
                }
                else{
                    CONNECTED_TO_SERVER = true;
                    log_message("Reconnected!");
                }
            }
            } else {
              Serial.println("An error ocurred");
            }
            http.end();
        }
        delay(1000);
    }
}

void check_connection(){
    HTTPClient http;
    http.begin(HOST + "/ping?mac_address=" + WiFi.macAddress());
    int httpCode = http.GET();

    if (httpCode > 0) {
        String payload = http.getString();
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, payload);
        if (!error) {
            String http_code = doc["code"];
            if (http_code != "200"){
                CONNECTED_TO_SERVER = false;
                log_message("Disconnected");
            }
            else{
                CONNECTED_TO_SERVER = true;
            }
        }
    } else {
        CONNECTED_TO_SERVER = false;
    }
}

void loop() {
    connect();
    check_connection();
    delay(1000);
}
