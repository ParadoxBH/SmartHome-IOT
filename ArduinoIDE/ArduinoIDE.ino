
int led = LED_BUILTIN;//Led interno do arduino uno
int led1 = 9;//Led interno do arduino uno
int led2 = 10;//Led interno do arduino uno
int led3 = 11;//Led interno do arduino uno
int led4 = 12;//Led interno do arduino uno
int led5 = 13;//Led interno do arduino uno

void setup() {
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  pinMode(led5, OUTPUT);

  ledStatus(led, false);
  ledStatus(led1, false);
  ledStatus(led2, false);
  ledStatus(led3, false);
  ledStatus(led4, false);
  ledStatus(led5, false);
}

//Acende ou Apaga um Led
void ledStatus(int led, bool status){
  digitalWrite(led, status?HIGH:LOW);
}

//Envia mensagem para a central
void serialSend(String texto){
  Serial.println(texto);
}

//Processa a mensagem recebida pela central
void processarMensagem(String texto)
{
  
  if(texto == "led_on")
    ledStatus(led,true);
  else if(texto == "led_off")
    ledStatus(led,false);

  else if(texto == "led1_on")
    ledStatus(led1,true);
  else if(texto == "led1_off")
    ledStatus(led1,false);

  else if(texto == "led2_on")
    ledStatus(led2,true);
  else if(texto == "led2_off")
    ledStatus(led2,false);

  else if(texto == "led3_on")
    ledStatus(led3,true);
  else if(texto == "led3_off")
    ledStatus(led3,false);

  else if(texto == "led4_on")
    ledStatus(led4,true);
  else if(texto == "led4_off")
    ledStatus(led4,false);

  else if(texto == "led5_on")
    ledStatus(led5,true);
  else if(texto == "led5_off")
    ledStatus(led5,false);

  serialSend(texto);
}

//Loop do programa
void loop() {
   while (Serial.available() > 0) 
   {     
    String serialMensagem = Serial.readString();  
    serialMensagem.trim();
    processarMensagem(serialMensagem);
  }
}
