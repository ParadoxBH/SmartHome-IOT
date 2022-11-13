from threading import Thread
import serial
import time

    
class ArduinoThead(Thread):

    def __init__ (self, read):
        Thread.__init__(self)
        self.runing = True
        self.read = read

    def run(self):
        while(self.runing):
            self.read()

    def stop(self):
        self.runing = False

class ArduinoEcho:
    def __init__(self, port, baud, receivedMenssageEvent):
        self.port = port
        self.baud = baud
        try:
            self.conect = serial.Serial(port, baud)
            print("Conexao com arduino estabelecida")
        except Exception as e:
            self.conect = None
            print("Erro de conexao com arduino")
        self.receivedMenssageEvent = receivedMenssageEvent
        self.thread = ArduinoThead(self.read)
        self.thread.start()
        pass

    def stopThread(self):
        self.runing = False
        self.thread.stop()
        pass

    #Enviar mensagem para arduino
    def write(self,text):
        try:
            if(self.conect == None):
                self.conect = serial.Serial(self.port, self.baud)
            if(self.conect == None):
                return False
            #self.conect.write(bytes(text, 'utf-8'))
            self.conect.write(text.encode())
            self.conect.flush()
            return True
        except:
            self.conect = None
            print("Falha na comunicação com o arduino")
        return False

    #Ler mensagem do arduino
    def read(self):
        try:
            if(self.conect == None):
                return
            msg = self.conect.readline()
            #msg = msg[2:-5]
            self.conect.flush()
            self.receivedMenssageEvent(str(msg))
        except:
            self.conect = None
            print("Erro de leitura")