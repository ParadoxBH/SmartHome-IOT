
int led = LED_BUILTIN;//Led interno do arduino uno

int buzzer = 2;//Pino da corneta do alarme
int luzsensor = A0;//Pino do sensor do laser
int laser = 3;//Pino do laser para o alarme

int led1 = 9;//Led interno do arduino uno
int led2 = 10;//Led interno do arduino uno
int led3 = 11;//Led interno do arduino uno
int led4 = 12;//Led interno do arduino uno
int led5 = 13;//Led interno do arduino uno

int delayBlink = 150;
int blinkMax = 5;
int cont =0;

void setup() {
  pinMode(led, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  pinMode(led5, OUTPUT);

  pinStatus(led, false);
  pinStatus(led1, false);
  pinStatus(led2, false);
  pinStatus(led3, false);
  pinStatus(led4, false);
  pinStatus(led5, false);
  
  pinMode(buzzer, OUTPUT);
  noTone(buzzer);

  pinMode(luzsensor, INPUT);

  pinMode(laser,OUTPUT);
  pinStatus(laser, false);
  
  delay(3000);
  Serial.begin(9600);
  blinkLed();
}

//Acende ou Apaga um Led
void pinStatus(int led, bool status){
  digitalWrite(led, status?HIGH:LOW);
}

//Envia mensagem para a central
void serialSend(String texto){
  Serial.println(texto);
}
//Envia mensagem para a central
void serialSend(int valor){
  Serial.println(valor);
}

void blinkLed(){
  
      pinStatus(led,false);
      pinStatus(led1,true);
      delay(delayBlink);
      
      pinStatus(led1,false);
      pinStatus(led2,true);
      delay(delayBlink);
      
      pinStatus(led2,false);
      pinStatus(led3,true);
      delay(delayBlink);
      
      pinStatus(led3,false);
      pinStatus(led4,true);
      delay(delayBlink);
      
      pinStatus(led4,false);
      pinStatus(led5,true);
      delay(delayBlink);
      
      pinStatus(led5,false);
      pinStatus(led,true);
      delay(delayBlink);
      pinStatus(led,false);

      
}

bool alarmeActive = false;
bool sensorStatus = false;
bool buzzerStatus = false;
bool acionarAlarme = false;
int buzzerDelay = 0;
bool buzzerSound = false;

void alarmeStatus(bool status)
{
    buzzerStatus = false;
    buzzerSound = false;
    noTone(buzzer);
    alarmeActive = status;
  pinStatus(laser, status);
  sensorStatus = true;
  delay(500);
}

int sensorValue = 0;
void alarmeLogic(){
  sensorValue = analogRead(luzsensor);
  if(sensorValue > 990)
    sensorStatus = true;
  else
    sensorStatus = false;

    if(alarmeActive == true && sensorStatus == false && buzzerStatus == false)
    {
      buzzerSound = true;
      buzzerStatus = true;
      pinStatus(laser, false);
      serialSend("alert");
    }

    if(buzzerStatus)
    {
      buzzerDelay = buzzerDelay + 1;
      if(buzzerDelay > 4){
        buzzerDelay = 0;
        buzzerSound = !buzzerSound;
        tone(buzzer, buzzerSound?392:440);
      }
    }

    delay(100);
}

//Processa a mensagem recebida pela central
void processarMensagem(String texto)
{
  
  if(texto == "ledblink_on")
  {
    cont =0 ;
    while(cont < blinkMax){
      blinkLed();
      cont++;
    }
      pinStatus(led,false);
  }
  else if(texto == "led_on")
    pinStatus(led,true);
  else if(texto == "led_off")
    pinStatus(led,false);

  else if(texto == "led1_on")
    pinStatus(led1,true);
  else if(texto == "led1_off")
    pinStatus(led1,false);

  else if(texto == "led2_on")
    pinStatus(led2,true);
  else if(texto == "led2_off")
    pinStatus(led2,false);

  else if(texto == "led3_on")
    pinStatus(led3,true);
  else if(texto == "led3_off")
    pinStatus(led3,false);

  else if(texto == "led4_on")
    pinStatus(led4,true);
  else if(texto == "led4_off")
    pinStatus(led4,false);

  else if(texto == "led5_on")
    pinStatus(led5,true);
  else if(texto == "led5_off")
    pinStatus(led5,false);
    
  else if(texto == "alarm_on")
    alarmeStatus(true);
  else if(texto == "alarm_off")
    alarmeStatus(false);

}

//Loop do programa
void loop() {
   while (Serial.available() > 0) 
   {     
    String serialMensagem = Serial.readString();  
    serialMensagem.trim();
    processarMensagem(serialMensagem);
  }
  alarmeLogic();
}
