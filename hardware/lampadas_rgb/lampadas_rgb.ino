//DECLARACAO DAS BIBLIOTECAS
#include <WiFi.h>         //Wi-Fi
#include <PubSubClient.h>     // MQTT
#include <time.h>             // UTC
#include <strings.h>          // String manipulation
#include <FS.h>               // Files
#include <ArduinoJson.h>

const int keys[] = {3, 2, 1, 6, 5, 4, 9, 8, 7, 0};
// ligar -1 acessar a posição do vetor que estara correto 
//Mapeação da ordem das lampadas // troca de 3 por 1,  nuemro da lampada pelo vetor 

//informações da rede WIFI
const char* ssid = "CSI-Lab"; //SSID da rede WIFI
const char* password =  "In@teLCS&I"; //senha da rede wifi

//informações do broker MQTT
const char* mqttServer = "192.168.66.11";   //servidor
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


#define PIN 5
#define NUMPIXELS 63
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#define DELAYVAL 50 // Time (in milliseconds) to pause between pixels

//FUNCAO DE RECEBIMENTO E PROCESSAMENTO DE MENSAGENS VINDAS DO BROKER
void callback(char* topic, byte* payload, unsigned int length){

  // Cria buffer seguro para a mensagem
  char msg[length + 1];

  memcpy(msg, payload, length);

  msg[length] = '\0';

  String topico = topic;

  Serial.println();
  Serial.println("-----------------------");

  Serial.print("Mensagem no tópico: ");
  Serial.println(topico);

  Serial.print("Mensagem recebida: ");
  Serial.println(msg);

  Serial.println("-----------------------");
  Serial.println();

  int rgb[3];

  // =========================
  // TOPICO VEIA
  // =========================
  if(topico == "rgb_module/veia/setLampState"){

    StaticJsonDocument<200> doc;

    DeserializationError error = deserializeJson(doc, msg);

    if (error) {

      Serial.print("Erro JSON: ");

      Serial.println(error.c_str());

      return;
    }

    int lamp = doc["lampada"];

    // Proteção
    if(lamp < 1 || lamp > 9){

      Serial.println("Lampada invalida");

      return;
    }

    rgb[0] = doc["r"];
    rgb[1] = doc["g"];
    rgb[2] = doc["b"];

    Serial.print("Lampada: ");
    Serial.println(lamp);

    Serial.print("R: ");
    Serial.println(rgb[0]);

    Serial.print("G: ");
    Serial.println(rgb[1]);

    Serial.print("B: ");
    Serial.println(rgb[2]);

    lampada(keys[lamp - 1], rgb);
  }

  // =========================
  // TOPICO DIMMER
  // =========================
  if (topico == "rgb_module/dimmer/setLampState"){

    StaticJsonDocument<200> doc;

    DeserializationError error = deserializeJson(doc, msg);

    if (error) {

      Serial.print("Erro JSON: ");

      Serial.println(error.c_str());

      return;
    }

    if (doc["dimmer"].isNull()){

      if (doc["right_hand_message"] == 0){

        rgb[0] = 0;
        rgb[1] = 0;
        rgb[2] = 0;
      }

      if (doc["right_hand_message"] == 1){

        rgb[0] = 255;
        rgb[1] = 255;
        rgb[2] = 255;
      }

      int lampNum = doc["left_hand"];

      lampada(keys[lampNum - 1], rgb);
    }

    if (doc["right_hand_message"].isNull()){

      rgb[0] = doc["dimmer"];
      rgb[1] = doc["dimmer"];
      rgb[2] = doc["dimmer"];

      int lampNum = doc["left_hand"];

      lampada(keys[lampNum - 1], rgb);
    }
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
  pinMode(5,OUTPUT);
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
