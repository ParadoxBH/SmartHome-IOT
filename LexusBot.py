from ast import Return
from asyncio.windows_events import NULL
import os
from os.path import exists as file_exists
import this
import json
from typing import Dict

import datetime
import time
# pip install--upgrade pip
# pip install pyserial
import serial

TOKEN = os.environ.get("TOKEN")
SERIAL = os.environ.get("SERIAL")

import TelegramAPI

class LexusBot:
    def __init__(self):
        self.data = {'users':{},'alarms':{}}
        try:
            self.arduino = serial.Serial(SERIAL, 9600)
        except:
            self.arduino = NULL
        self.cargoNome = ["Convidado","Usuario", "Administrador"]
        pass

    #Enviar mensagem para arduino
    def arduinoWrite(self,text):
        try:
            if(self.arduino == NULL):
                return
            #self.arduino.write(bytes(text, 'utf-8'))
            self.arduino.write(text.encode())
            self.arduino.flush()
        except:
            self.arduino = NULL

    #Ler mensagem do arduino
    def arduinoRead(self):
        try:
            if(self.arduino == NULL):
                return ""
            time.sleep(0.05)
            msg = self.arduino.readline()
            #msg = msg[2:-5]
            self.arduino.flush()
            return msg
        except:
            self.arduino = NULL
            return ""
    
    def receivedMenssageEvent(self, Mensagem):
        atualUser = self.getUser(Mensagem)
        mensagemAtual = Mensagem.texto.split(' ')
        mensagemSize = len(mensagemAtual)
        if atualUser["cargo"] >= 0:#Comandos Convidado
            if (mensagemAtual[0] == "/cadastrar" and atualUser["cargo"] == 0):
                return self.requestRegistration(Mensagem)

        if atualUser["cargo"] >= 1:#Comandos Usuario
            if mensagemAtual[0] == "/luz":
                if mensagemSize >= 2 and mensagemAtual[1] == "on":
                    self.telegramAPI.sendMensagem(Mensagem,"O led foi acesso")
                    return self.arduinoWrite("led_on")
                if mensagemSize >= 2 and mensagemAtual[1] == "off":
                    self.telegramAPI.sendMensagem(Mensagem,"O led foi apagado")
                    return self.arduinoWrite("led_off")
                texto = "o comando /luz aceita as seguintes combinações:\n"
                texto += "/luz on - Liga a luz\n"
                texto += "/luz off - Desliga a luz\n"
                return self.telegramAPI.sendMensagem(Mensagem,texto)

        if atualUser["cargo"] >= 2:#Comandos ADM
            if mensagemAtual[0] == "/user":
                if mensagemSize >= 2 and mensagemAtual[1] == "list":
                    return self.telegramAPI.sendMensagem(Mensagem,self.getListUsers())
                if mensagemSize >= 4 and (mensagemAtual[1] == "add" or mensagemAtual[1] == "update"):
                    if mensagemAtual[2] == "usuario":
                        return self.addUser(Mensagem,1,mensagemAtual[3])
                    if mensagemAtual[2] == "adm":
                        return self.addUser(Mensagem,2,mensagemAtual[3])
                if mensagemSize >= 2 and mensagemAtual[1] == "remove":
                    return self.removeUser(Mensagem, mensagemAtual[2])
                texto = "O comando /user aceita as seguintes combinações:\n"
                texto += "/user [add|update] [usuario|adm] [id] - Adiciona um usuario a o sistema\n"
                texto += "/user remove [id] - Remove um usuario a o sistema\n"
                texto += "/user list - Listar todos presentes no sistema\n"
                return self.telegramAPI.sendMensagem(Mensagem,texto)


        if mensagemAtual[0] == "/help" or mensagemAtual[0] == "/start":
            return self.telegramAPI.sendMensagem(Mensagem,self.getHelpText(atualUser))


        self.telegramAPI.sendMensagem(Mensagem,"Desculpe, não compreendi sua mensagem.\nVocê poderia tentar /help para ter mais informações do que sou capaz de fazer.")
        pass
    
    def requestRegistration(self, Mensagem):
        if Mensagem.id in self.data["users"]:
            return self.telegramAPI.sendMensagem(Mensagem,"Sua solitação está em processamento, por favor aguarde até que um dos nossos administradores confirme seu cadastro.")
          
        self.sendMensagemADM("{id} - {nome} solicitou acesso a aplicação. Oque deseja fazer?\n/user add convidado {id} - Aceitar\n/user remove {id} - Recusar".format(id=Mensagem.id,nome=Mensagem.nome))
        print(self.data["users"])
        self.data["users"][Mensagem.id] = self.User(Mensagem)
        print(self.data["users"])
        self.telegramAPI.sendMensagem(Mensagem,"Solicitação envida com sucesso.\nEm breve um dos nossos administradores irá confirmar seu cadastro.")
        self.saveJson()
        pass
    
    def addUser(self, Mensagem, cargo, id):

        if Mensagem.id in self.data["users"] and self.data["users"][Mensagem.id]["cargo"] < cargo:
            return self.telegramAPI.sendMensagem(Mensagem,"Não é possivel dar um cargo maior que o seu para um usuario")
        elif id in self.data["users"]:
            if self.data["users"][id]["cargo"] >= (Mensagem.id in self.data["users"] and self.data["users"][Mensagem.id]["cargo"] or 2):
                return self.telegramAPI.sendMensagem(Mensagem,"Não é possivel alterar o cargo deste usuario pois o mesmo tem um cargo maior que o seu.")
            self.telegramAPI.sendMensagem(Mensagem,"Foi alterado o cargo do '{nome}' de {old} para {new}.".format(nome=self.data["users"][id]["nome"],old=self.stringCargo(self.data["users"][id]["cargo"]),new=self.stringCargo(cargo)))
            self.data["users"][id]["cargo"] = cargo
        else:
            self.data["users"][id] = self.UserData(id,"Desconhecido",cargo)
            self.telegramAPI.sendMensagem(Mensagem,"O '{id}' foi adicionado como {cargo}.".format(id=id,cargo=self.stringCargo(cargo)))
            MensagemNovoUsuario = TelegramAPI.Mensagem(NULL)
            MensagemNovoUsuario.id = id
        self.telegramAPI.sendMensagem(MensagemNovoUsuario,"Olá você foi adicionado por um dos nossos administradores como {cargo}.".format(id=id,cargo=self.stringCargo(cargo)))
        self.saveJson()
    
    def removeUser(self, Mensagem, id):
        if id in self.data["users"]:
            if self.data["users"][id]["cargo"] >= (Mensagem.id in self.data["users"] and self.data["users"][Mensagem.id]["cargo"] or 2):
                return self.telegramAPI.sendMensagem(Mensagem,"Não é possivel remover este usuario pois o mesmo tem um cargo maior maior que o seu.")
            else:
                self.telegramAPI.sendMensagem(Mensagem,"{nome} foi 'promovido' para {cargo}".format(nome=self.data["users"][id]["nome"],cargo=self.stringCargo(0)))
                del self.data["users"][id]
                return self.saveJson()
        else:
            self.telegramAPI.sendMensagem(Mensagem," O id '{id}' não é usuario".format(id=id))
          
    def stringCargo(self,cargo):
        if cargo < len(self.cargoNome):
            return self.cargoNome[cargo]
        return self.cargoNome[len(self.cargoNome)-1]

    def User(self,Mensagem):
        return self.UserData(Mensagem.id,Mensagem.nome,0)
            
    def UserData(self,id,nome,cargo):
        return {
                'id': id,
                'nome': nome,
                'cargo': cargo,
            }

    #Converte a mensagem recebida em parametro de usuario
    def getUser(self, Mensagem):
        retorno = self.User(Mensagem)
        if Mensagem.id in self.data["users"]:
            retorno["cargo"] = self.data["users"][Mensagem.id]["cargo"]
            if self.data["users"][Mensagem.id]["nome"] != Mensagem.nome:
                self.saveJson()
            self.data["users"][Mensagem.id]["nome"] = Mensagem.nome
        return retorno

    #Retorna a listagem de todos os usuarios cadastrados
    def getListUsers(self):
        texto = "Segue a lista dos usuario cadastrados:"

        convidados = []
        usuarios = []
        adm = []

        for x in self.data["users"]:
            if self.data["users"][x]["cargo"] == 0:
                convidados.append(self.data["users"][x]["id"] + " - " + self.data["users"][x]["nome"])
            if self.data["users"][x]["cargo"] == 1:
                usuarios.append(self.data["users"][x]["id"] + " - " + self.data["users"][x]["nome"])
            if self.data["users"][x]["cargo"] >= 2:
                adm.append(self.data["users"][x]["id"] + " - " + self.data["users"][x]["nome"])
        

        texto += "\n\n[{cargo} ({cont})]:".format(cargo=self.stringCargo(0), cont=len(convidados))
        for x in convidados:
            texto += "\n" + x

        texto += "\n\n[{cargo} ({cont})]:".format(cargo=self.stringCargo(1), cont=len(usuarios))
        for x in usuarios:
            texto += "\n" + x

        texto += "\n\n[{cargo} ({cont})]:".format(cargo=self.stringCargo(2), cont=len(adm))
        for x in adm:
            texto += "\n" + x

        return texto

    #Retorna a mensagem de Ajuda
    def getHelpText(self, atualUser):
        texto = "Eu respondo a os seguintes comandos:\n\n"
        if atualUser["cargo"] == 0:#Comandos Anonimo
            texto += "/cadastrar - Solicita a um administração para lhe dar acesso a o sistema\n"
            pass
        if atualUser["cargo"] >= 1:#Comandos Convidado
            texto += "/luz [on|off]- Acende ou Apaga a luz\n"
            pass
        if atualUser["cargo"] >= 2:#Comandos ADM
            texto += "/user - Gerencia usuarios\n"
            pass
        texto += "/help - Lista de comandos\n"
        return texto

    def sendMensagemADM(self, texto):
        print(texto)
        print("-" * os.get_terminal_size().columns)
        pass

    #Roda a class
    def run(self):
        self.loadJson()
        self.telegramAPI = TelegramAPI.TelegramEcho(TOKEN, self.receivedMenssageEvent)
        self.telegramAPI.run()
        pass

    def saveJson(self):
        print("\tSalvando .json")
        print("-" * os.get_terminal_size().columns)
        file = open("data.json", "w")
        dataSave = json.dumps(self.data)
        file.write(dataSave)
        file.close()
        return

    def loadJson(self):
        if not os.path.exists("data.json"):
            return
        file = open("data.json","r")
        try:
            dataJson = file.read()
            self.data = json.loads(dataJson)
        except:
            pass
        file.close()
        pass

#Função inicial do programa
if __name__ == "__main__":
    
    print("-" * os.get_terminal_size().columns)
    print("\tINICIALIZANDO LEXUS")
    print("-" * os.get_terminal_size().columns)


    tg = LexusBot()
    tg.run()
    
    """
    #RUN AS ANTIBUG
    while(True):
        try:
            tg = LexusBot()
            tg.run()
        except Exception as e:
            print("Um erro inesperado aconteceu:")
            print(e)
            print("-" * os.get_terminal_size().columns)
            print("\tREINICIANDO LEXUS")
            print("-" * os.get_terminal_size().columns)
    """
