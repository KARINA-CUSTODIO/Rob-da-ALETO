from flask import Flask
import os

import requests
from flask import Flask, request
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

def projetos(limite=10):
  # extraindo projetos de Lei e requerimentos
  resposta = requests.get('https://al.to.leg.br/materiasLegislativas')
  sopa = BeautifulSoup(resposta.content, 'html.parser')
  PLs = sopa.findAll('div', {'class':'row'}) 
  contador = 0
  PL = []
  for pl in PLs:
    if contador == limite:
      break
    try:
      titulo = pl.find('h4').text
      data = pl.find('p').text.split('|')[1].split(':')[1].strip()
      texto = pl.find_all('div', class_= 'col-12')[-1].text
      path = pl.find('a').attrs['href']
      url = f'https://al.to.leg.br{path}'
      mensagem = f"{titulo} {data} \n {texto} \n {url} \n"
      PL.append(mensagem)
      contador += 1
    except AttributeError:
      print(mensagem)
  return PL

# Criando site

app = Flask(__name__)

menu = """
<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> | <a href="/gastos">Gastos</a> | <a href="/contato">Contato</a> | <a href="/telegram">Telegram</a>
<br>
"""

@app.route("/sobre")
def sobre():
  return menu + "Aqui vai o conteúdo da página Sobre"

@app.route("/contato")
def contato():
  return menu + "Aqui vai o conteúdo da página Contato"

@app.route("/telegram", methods=["POST"])

def telegram_bot():
    update = request.json
    if 'message' in update:
      chat_id = update["message"]["chat"]["id"]
      message = update["message"]["text"]
      message = message.strip().lower()
      first_name = update["message"]["from"]["first_name"]
      sender_id = update["message"]["from"]["id"]
     
      PL = projetos()
       
      mensagens = ['oi', 'Oi', 'Olá', 'olá', 'ola', 'iai', 'qual é', 'e aí', "/start"]
      if message in mensagens:
        texto_resposta = f"Olá! Seja bem-vinda(o) {first_name}! Digite sim caso queira ver os últimos PLs da Assembleia Legislativa do Tocantins!"
      elif message == 'sim':
        texto_PLs = ""
        for pl in PL:
            texto_PLs += pl + "\n\n"
            texto_resposta = texto_PLs
    else:
        texto_resposta = "Não entendi!"
    
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
    print(resposta.text)
    return "ok"
