#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#define  engine1_port D0

String unique_key = "XtVT7Fy8jQ";
String HOST = "http://192.168.1.10:8090";
bool CONNECTED_TO_SERVER = false;
bool built_in_led1_is_on = false;
bool built_in_led2_is_on = false;
bool autoPing = true;
bool run_show = false;

WiFiServer wifiServer(80);
WiFiClient client;

int show_size = 0;
String show_elements[1300];
int next_show_elem_time = 0;
int next_show_elem_index = 0;
int show_start_time = 0;

String res = "";
long timing = 0;

void next_show_elem(){
    if (next_show_elem_index < show_size){

        Serial.println(next_show_elem_index);

        // Получаем элемент  '{'cd':"...", "t":123}'
        String show_elem = show_elements[next_show_elem_index];

        // Дешифруем элемент  {'cd':"...", "t":123}
        DynamicJsonDocument current_element(1024);
        deserializeJson(current_element, show_elem);

        // Получаем команду  "{"b_led2": 0}"
        String current_command_json_string = current_element["cd"];

        // Дешифруем команду  {"b_led2": 0}
        DynamicJsonDocument current_command(1024);
        deserializeJson(current_command, current_command_json_string);

        if (current_command.containsKey("b_led1")) {
            if (current_command["b_led1"] == 1){
                built_in_led1_is_on = false;
                Serial.println("en1");
            } else {
                built_in_led1_is_on = true;
                Serial.println("dn1");
            }
        }

        if (current_command.containsKey("b_led2")) {
            if (current_command["b_led2"] == 1){
                built_in_led2_is_on = false;
                Serial.println("en2");
            } else {
                built_in_led2_is_on = true;
                Serial.println("dn2");
            }
        }
        Serial.println("passed 1");
        if(next_show_elem_index + 1 < show_size){
            next_show_elem_index += 1;

            // Получаем следующий элемент '{'cd':"...", "t":125}'
            String next_show_elem_json_string = show_elements[next_show_elem_index];

            // Дешифруем следующий элемент  {'cd':"...", "t":125}
            DynamicJsonDocument next_show_elem(1024);
            deserializeJson(next_show_elem, next_show_elem_json_string);

            next_show_elem_time = next_show_elem["t"];

            Serial.println(String(next_show_elem_time));
            Serial.println("passed 2");
        } else {
            run_show = false;
        }
    } else {
            run_show = false;
    }

}

void setup () {

  Serial.begin(115200);
  WiFi.begin("sweet home", "05051979");
  pinMode(engine1_port, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, LOW);
  while (WiFi.status() != WL_CONNECTED) {

    delay(1000);
    Serial.println("Connecting..");

  }
  Serial.println("Connected to WiFi Network");
  connect();
  check_connection();
  Serial.println(WiFi.localIP());
  digitalWrite(LED_BUILTIN, HIGH);
  wifiServer.begin();
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
    String request = HOST + "/ping?mac_address=" + WiFi.macAddress();
    if(run_show){
        request += "&rs=1";
    } else {
        request += "&rs=0";
    }
    request += "&ss=" + String(show_size);
    request += "&time=" + String(millis());
    request += "&nei=" + String(next_show_elem_index);
    request += "&net=" + String(next_show_elem_time);
    request += "&stt=" + String(show_start_time);

    http.begin(request);

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



    // Чтение информации из сокетов
    if (!client.connected()) {
        client = wifiServer.available();
    } else {
        if (client.available() > 0) {
            res += char(client.read());
        } else if (res != "") {
            Serial.println(res);
            if (res != "") {
                Serial.println("r");
                client.write("ok");

                DynamicJsonDocument doc(1024);
                deserializeJson(doc, res);

                // Команды
                if (doc.containsKey("mp")) {
                    if (doc["mp"] == 1){
                        Serial.println("MANUAL PING");
                        autoPing = false;
                    } else {
                        autoPing = true;
                        Serial.println("AUTO PING");
                        Serial.println(millis());
                        Serial.println(next_show_elem_time + show_start_time);
                    }
                }

                // Загрузка шоу на аэростат
                if (doc.containsKey("ss")) {
                    show_size = doc["ss"];
                    Serial.println("SETTED SHOW SIZE");
                }

                if (doc.containsKey("se")) {
                    int element_index = doc["ei"];
                    String new_show_element = doc["se"];
                    show_elements[element_index] = new_show_element;
                    Serial.println(String(element_index));
                    Serial.println(String(new_show_element));
                }

                if (doc.containsKey("rs")) {
                  Serial.println("start");
                    if(doc["rs"] == 1){
                        Serial.println("START1");
                        run_show = true;
                        show_start_time = millis();
                        next_show_elem_index = 0;
                        next_show_elem_time = 0;
                        Serial.println("START2");
                    } else {
                        run_show = false;
                    }

                }

                // Динамическое управление
                if (doc.containsKey("b_led1")) {
                    if (doc["b_led1"] == 1){
                        built_in_led1_is_on = true;
                    } else {
                        built_in_led1_is_on = false;
                    }
                }

                if (doc.containsKey("b_led2")) {
                    if (doc["b_led2"] == 1){
                        built_in_led2_is_on = true;
                    } else {
                        built_in_led2_is_on = false;
                    }
                }
                res = "";
            }
        }
    }

    if (autoPing && (millis() - timing > 3000)){
        timing = millis();
        check_connection();
        connect();
        Serial.println(millis());
        Serial.println(next_show_elem_time + show_start_time);
    }

    if (run_show && (millis() >= (next_show_elem_time + show_start_time))){
        Serial.println("NEXT");
        next_show_elem();
    }

   if(built_in_led1_is_on){
      digitalWrite(LED_BUILTIN, LOW);
    } else {
      digitalWrite(LED_BUILTIN, HIGH);
   }

   if(built_in_led2_is_on){
      digitalWrite(engine1_port, HIGH);
    } else {
      digitalWrite(engine1_port, LOW);
   }
}
