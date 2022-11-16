import urllib.request as request
from urllib.error import HTTPError
from http.client import HTTPResponse
from typing import Dict, List, Union
import json
from datetime import datetime
import signal
import os
import time

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Mensagem:
    def __init__(self, incoming):
        try:
            self.id = str(incoming["message"]["chat"]["id"])
            self.cont = incoming["message"]["message_id"]
            self.data = datetime.fromtimestamp(incoming["message"]["date"])
            self.dataString = self.data.strftime("%Y-%m-%d %H:%M:%S")
            try:
                self.username = incoming["message"]["from"]["username"]
                self.nome = self.username
                self.texto = ""
            except:
                self.username = str(self.id)
                self.nome = (incoming["message"]["from"].get("first_name", "") + " " + incoming["message"]["from"].get("last_name", ""))
                self.texto = incoming["message"]["text"]
        except:
            self.id = "0"
            self.cont = "0"
            self.data = datetime.fromtimestamp(time.time())
            self.dataString = "00/00/00 00:00:00"
            self.username = "0"
            self.nome = ""
            self.texto = ""
        pass

    def printInf(self):
        try:
            print("De {nome} as {tempo}".format(nome=self.nome,tempo=self.dataString))
            print(self.texto)
            print("-" * os.get_terminal_size().columns)
        except:
            print("erro na impressao da mensagem")
        pass


class TelegramEcho:
    def __init__(self, TG_KEY: str, receivedMenssageEvent):
        self.TG_URL = "https://api.telegram.org/bot{key}/{method}"
        self.TG_KEY = TG_KEY
        self.receivedMenssageEvent = receivedMenssageEvent
        self.lastresults = ""
        self.__last = None
        self.__last_time = None
        pass

    def sendMensagem(self, usuario: Mensagem, texto: str):
        print("Para {nome} as {tempo}".format(nome=usuario.nome,tempo=time.strftime("%H:%M:%S")))
        print(texto)
        print("-" * os.get_terminal_size().columns)
        self.__handle_outgoing(usuario.id,texto)
        pass

    def run(self):
        """
        method to handle the incoming message and the send echo message to the user
        """
        while True:
            try:
                # getting the incoming data
                incoming = self.__handle_incoming()

                # checking if incoming message_id is same as of last, then skip
                if self.__last == incoming["message"]["message_id"]:
                    continue
                else:
                    self.__last = incoming["message"]["message_id"]

                # adding more validation to prevent messaging the last message whenever the polling starts
                if not self.__last_time:
                    self.__last_time = incoming["message"]["date"]
                    continue
                elif self.__last_time < incoming["message"]["date"]:
                    self.__last_time = incoming["message"]["date"]
                else:
                    continue

                novaMensagem = Mensagem(incoming)
                novaMensagem.printInf()
                self.receivedMenssageEvent(novaMensagem)

                pass
            except (HTTPError, IndexError):
                continue
            pass
        pass

    def __handle_incoming(self) -> Dict[str, Union[int, str]]:
        """
        method fetch the recent messages
        """

        # getting all messages
        getUpdates = request.urlopen(
            self.TG_URL.format(key=self.TG_KEY, method="getUpdates?offset=-1"))

        # parsing results
        results: List[Dict[str, Union[int, str]]] = json.loads(
            getUpdates.read().decode())["result"]

        # getting the last error
        return results[-1]

    

    def __handle_outgoing(self, chat_id: int, message_txt: str) -> Dict[str, Union[int, str]]:
        """
        method to send the echo message to the same chat
        """

        # making the post data
        _data: Dict[str, Union[int, str]] = {
            "chat_id":
            chat_id,
            "text":
            message_txt
        }

        # creating the request
        _request: request.Request = request.Request(
            self.TG_URL.format(key=self.TG_KEY, method="sendMessage"),
            data=json.dumps(_data).encode('utf8'),
            headers={"Content-Type": "application/json"})

        # sending HTTP request, for sending message to the user
        sendMessage: HTTPResponse = request.urlopen(_request)
        result: Dict[str, Union[int, str]] = json.loads(
            sendMessage.read().decode())["result"]
        return result

    pass
