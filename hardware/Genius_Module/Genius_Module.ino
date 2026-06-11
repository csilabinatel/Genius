//DECLARACAO DAS BIBLIOTECAS
#include <ESP8266WiFi.h> 
#include <PubSubClient.h>    
#include <time.h>             
#include <strings.h>          
#include <FS.h>               
#include <ArduinoJson.h>

//informações da rede WIFI
const char* ssid = "CSI-Lab"; 
const char* password =  "In@teLCS&I"; 

//informações do broker MQTT
const char* mqttServer = "192.168.66.11";   
const char* mqttUser = "csilab";            
const char* mqttPassword = "WhoAmI#2024";  
const int mqttPort = 1883;              
const char* mqttTopicSub = "lamp_module/#";  
const char *ID = "Futurecom_01";

#define lamp1    16 //D0
#define lamp2    5  //D1
#define lamp3    4  //D2
#define lamp4    0  //D3
#define lamp5    14 //D4
#define lamp6    2  //D5

WiFiClient espClient;
PubSubClient client(espClient);


//função lampada 
void lampada (int lamp, int estado){

  if(estado == 1)
    estado = 0;
  
  else
    estado = 1;

  switch(lamp){
    case 1:
      digitalWrite(lamp1,estado);
      break;
    case 2:
      digitalWrite(lamp2,estado);
      break;
    case 3:
      digitalWrite(lamp3,estado);
      break;
    case 4:
      digitalWrite(lamp4,estado);
      break;
    case 5:
      digitalWrite(lamp5,estado);
      break;
    case 6:
      digitalWrite(lamp6,estado);
      break;
    default:
     break;
  }

}

//FUNCAO DE RECEBIMENTO E PROCESSAMENTO DE MENSAGENS VINDAS DO BROKER
void callback(char* topic, byte* payload, unsigned int length){
  String topico = topic;

  if (topico == "lamp_module/setState"){
    char msg[length + 1];
    memcpy(msg, payload, length);
    msg[length] = '\0';
    StaticJsonDocument<200> doc; // Deserializa a string JSON para o objeto doc
    DeserializationError error = deserializeJson(doc, msg); // Verifica se houve erro na deserialização
    if (error) {
      Serial.print(F("Falha na deserialização: "));
      Serial.println(error.f_str());
      return;
    }
    
    int lamp = doc["lampada"];
    int estado = doc["estado"];
    Serial.println(String(lamp)+" - "+String(estado));
    lampada(lamp,estado);
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
  Serial.begin(115200); //Velocidade da Serial

  pinMode(lamp1, OUTPUT); //pino da lâmpada 1 como saída
  pinMode(lamp2, OUTPUT); //pino da lâmpada 2 como saída
  pinMode(lamp3, OUTPUT); //pino da lâmpada 3 como saída
  pinMode(lamp4, OUTPUT); //pino da lâmpada 4 como saída
  pinMode(lamp5, OUTPUT); //pino da lâmpada 5 como saída
  pinMode(lamp6, OUTPUT); //pino da lâmpada 6 como saída

  digitalWrite(lamp1, 1); //Apagando-as
  digitalWrite(lamp2, 1);
  digitalWrite(lamp3, 1);
  digitalWrite(lamp4, 1);
  digitalWrite(lamp5, 1);
  digitalWrite(lamp6, 1);

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

void loop(){
  client.loop();
  delay(100);

  if (!client.connected())
  {
    connect();

  }
}
