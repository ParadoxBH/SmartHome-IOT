
int led = LED_BUILTIN;//Led interno do arduino uno

void setup() {
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  ledStatus(led,false);
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
void processarMensagem(String texto){
  if(texto == "led_on")
    ledStatus(led,true);
  else if(texto == "led_off")
    ledStatus(led,false);
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
