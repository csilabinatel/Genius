//DECLARACAO DAS BIBLIOTECAS
#include <ESP8266WiFi.h>      // Wi-Fi
#include <PubSubClient.h>     // MQTT
#include <time.h>             // UTC
#include <strings.h>          // String manipulation
#include <FS.h>               // Files
#include <ArduinoJson.h>

const int keys[] = {3, 2, 1, 6, 5, 4, 9, 8, 7, 0};

//informações da rede WIFI
const char* ssid = "CSI-Lab"; //SSID da rede WIFI
const char* password =  "In@teLCS&I"; //senha da rede wifi

//informações do broker MQTT
const char* mqttServer = "192.168.40.7";   //servidor
const char* mqttUser = "csilab";              //usuário
const char* mqttPassword = "WhoAmI#2024";      //senha
const int mqttPort = 1883;                     //porta
const char* mqttTopicSub = "rgb_module/#";           //tópico que sera assinado
const char *ID = "Futurecom_01231231";  // Name of our device, must be unique

WiFiClient espClient;
PubSubClient client(espClient);

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif


#define PIN D2
#define NUMPIXELS 63
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#define DELAYVAL 50 // Time (in milliseconds) to pause between pixels

//FUNCAO DE RECEBIMENTO E PROCESSAMENTO DE MENSAGENS VINDAS DO BROKER
void callback(char* topic, byte* payload, unsigned int length){
  //armazena mensagem recebida em uma variavel inteira
  payload[length] = '\0';
  int MSG = atoi((char*)payload);
  String topico = topic;
  
  Serial.println();
  Serial.println("-----------------------");

  //MOSTRANDO RECEBIMENTO DA MENSAGEM NA SERIAL
  Serial.print("Mensagem no tópico: ");
  Serial.println(topico);
  Serial.print("Mensagem:");
  Serial.print(MSG);

  Serial.println();
  Serial.println("-----------------------");
  Serial.println();

  int rgb[3];

  //{"lampada":1,"r":0,"g":0,"b":0} exemplo de mensagem recebida
  if (topico == "rgb_module/dimmer/setLampState"){
    const char* msg = (char*)payload; // Define o tamanho do buffer necessário para armazenar o JSON
    StaticJsonDocument<200> doc; // Deserializa a string JSON para o objeto doc
    DeserializationError error = deserializeJson(doc, msg); // Verifica se houve erro na deserialização
    if (error) {
      Serial.print(F("Falha na deserialização: "));
      Serial.println(error.f_str());
      return;
    }

    if (doc["dimmer"].isNull()){
      if (doc["right_hand_message"] == 0) { rgb[0] = 0; rgb[1] = 0; rgb[2] = 0; }
      if (doc["right_hand_message"] == 1) { rgb[0] = 255; rgb[1] = 255; rgb[2] = 255;}
      int lampNum = doc["left_hand"];
      lampada(keys[lampNum-1],rgb);
    }
    if (doc["right_hand_message"].isNull()){
      rgb[0] = doc["dimmer"]; rgb[1] = doc["dimmer"]; rgb[2] = doc["dimmer"];
      int lampNum = doc["left_hand"];
      lampada(keys[lampNum-1],rgb);
    }
  }
  if(topico == "rgb_module/veia/setLampState"){
    const char* msg = (char*)payload; // Define o tamanho do buffer necessário para armazenar o JSON
    StaticJsonDocument<200> doc; // Deserializa a string JSON para o objeto doc
    DeserializationError error = deserializeJson(doc, msg); // Verifica se houve erro na deserialização
    if (error) {
      Serial.print(F("Falha na deserialização: "));
      Serial.println(error.f_str());
      return;
    }
    rgb[0] = doc["r"];
    rgb[1] = doc["g"];
    rgb[2] = doc["b"];
    lampada(doc["lampada"],rgb);
  }
}
  
void connect () //FUNCAO DE RECONEXAO COM O BROKER
{
  while (!client.connected()) //enquanto a conexão com o broker não for realizada
  {
    Serial.println("Conectando ao Broker MQTT...");

    if (client.connect(ID, mqttUser, mqttPassword )) {
      Serial.println("Conectado");
    }
    else
    {
      Serial.print("falha estado  ");
      Serial.print(client.state());
      delay(2000);
    }
  }
  //subscreve no tópico
  client.subscribe(mqttTopicSub);
}

void setup()
{
  pinMode(D2,OUTPUT);
  Serial.begin(115200); //Velocidade da Serial

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)

  Serial.println("------Conexao WI-FI------");
  Serial.print("Conectando-se na rede: ");
  Serial.println(ssid);
  Serial.println("Aguarde");

  if (WiFi.status() == WL_CONNECTED)
    return;

  WiFi.begin(ssid, password); // Conecta na rede WI-FI

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Conectado com sucesso na rede ");
  Serial.print(ssid);

  //SETTING MQTT SERVER AND CALLBACK
  Serial.print(String(mqttServer)+" "+String(mqttPort));
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  Serial.print("\nMQTT connecting... \n");
  connect();
}

void lampada(int lamp, int rgb[3]){
  for(int i= (lamp - 1)*7; i < lamp*7; i++){
    pixels.setPixelColor(i, pixels.Color(rgb[0], rgb[1], rgb[2]));
    pixels.show();   // Send the updated pixel colors to the hardware.
  }
}

void loop(){
  //pixels.clear(); // Set all pixel colors to 'off'
  client.loop();
  delay(100);

  if (!client.connected())
  {
    connect();

  }
}