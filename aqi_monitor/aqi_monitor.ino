// config file
#include "config.h"

// basics
#include <ArduinoJson.h>
#include "base64.h"

// wifi
#include <ESP8266WiFi.h>

#include <WiFiClient.h>
#include <WiFiClientSecure.h>

// sds
#include <NovaSDS011.h>

// bme 
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>


// pin mapping
#define SDS_PIN_RX D7
#define SDS_PIN_TX D8
#define BME_SCK D1
#define BME_MISO D4
#define BME_MOSI D2
#define BME_CS D3


// initiate devices
NovaSDS011 sds011;
Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI


// build base64 auth string
String auth = base64::encode(String(authUsername) + ":" + String(authPassword));


void setup() {
  Serial.begin(9600);
  delay(500);
  Serial.println();

  // initiate device
  sds011.begin(SDS_PIN_RX, SDS_PIN_TX);

  
  if (sds011.setWorkingMode(WorkingMode::work)) {
    Serial.println("SDS011 working mode \"Work\"");
  } else {
    Serial.println("FAIL: Unable to set working mode \"Work\"");
  }

  // main loop speed
  if (sds011.setDutyCycle(2)) {
    Serial.println("SDS011 Duty Cycle set to 2min");
  } else {
    Serial.println("FAIL: Unable to set Duty Cycle");
  }
  delay(1000);

  // BME setup
  // default settings
  bool status;
  status = bme.begin();
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
  }

  // wifi setup
  Serial.println("connecting to wifi");

  WiFiClient client;
  WiFi.begin(ssid, password);
  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  
  int retries = 0;
  while ((WiFi.status() != WL_CONNECTED) && (retries < 20)) {
     retries++;
     delay(1000);
     Serial.print(".");
  }
  if (retries >= 20) {
    Serial.println(F("WiFi connection FAILED"));
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(F("WiFi connected!"));
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }
  Serial.println(F("Setup ready"));

}


void loop() {
  // setup vars
  float pm25, pm10, temperature, pressure, humidity;
  int uptime;
  int reconnects = 0;
  // wait until no errors to print values
  if (sds011.queryData(pm25, pm10) == QuerryError::no_error) {

    uptime = millis() / 1000;
    // bme vars
    temperature = bme.readTemperature();
    pressure = bme.readPressure() / 100.0F;
    humidity = bme.readHumidity();

    // build JSON
    StaticJsonDocument<200> doc;

    doc["uptime"] = uptime;
    doc["temperature"] = temperature;
    doc["pressure"] = pressure;
    doc["humidity"] = humidity;
    doc["pm25"] = pm25;
    doc["pm10"] = pm10;

    // send data
    String response;
    
    if (WiFi.status() == WL_CONNECTED) {
      
      // format json body
      String requestBody;
      serializeJson(doc, requestBody);
      Serial.println(requestBody);

      // connect to remote
      WiFiClientSecure client;
      client.setInsecure();
      char host[] = "data.lpb-air.com";

      // retry on error
      int retry = 0;
      while ((!client.connect(host, 443)) && (retry < 5)) {
        delay(1000);
        Serial.print(".");
        retry++;
      }
      if (retry == 5) {
        Serial.println("Connection failed");
      }
      // build request
      client.print(String("POST ") + "/ingest" + 
                  " HTTP/1.1\r\n" + 
                  "Host: " + host + "\r\n" + 
                  "Authorization: Basic " + auth + "\r\n" +
                  "Connection: close\r\n" + 
                  "Content-Length: " + requestBody.length() + "\r\n" + 
                  "Content-Type: application/json;charset=UTF-8\r\n\r\n" + 
                  requestBody + "\r\n");
      
      // read response
      while (client.connected()) {
        String line = client.readStringUntil('\n');
        if (line == "\r") {
          break;
        }
      }
      while (client.available()) {
        response += client.readStringUntil('\n');
      }
      Serial.println(response);
      
    } else {
      
      // wifi problems
      Serial.println("wifi not connected");
      WiFi.disconnect();
      WiFi.reconnect();
      reconnects ++;
      // try reconnecting
      while (WiFi.status() != WL_CONNECTED && reconnects < 10 ) {
        delay(2000);
        Serial.print(".");
        reconnects ++;
      }
      // restart if all failed
      if (WiFi.status() == WL_CONNECTED) {
        ESP.restart();
      }
      
    }
    
    delay(60000);
    
  }
}
