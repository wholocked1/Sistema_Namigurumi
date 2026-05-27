import os
import time
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from database import DatabaseCSV
from dotenv import load_dotenv

load_dotenv()
# ==========================================
# CONFIGURAÇÕES DO SEU E-MAIL
# ==========================================
MEU_EMAIL = os.getenv("EMAIL_BOT")  
MINHA_SENHA = os.getenv("SENHA_BOT")

ASSUNTO_GATILHO = "Ping Compras"

def gerar_texto_lista_compras():
    db = DatabaseCSV()
    estoque = db.carregar_materiais()
    
    em_falta = [m for m in estoque.values() if m.quantidade <= 0]
    acabando = [m for m in estoque.values() if m.quantidade == 1]
    
    if not em_falta and not acabando:
        return "Seu estoque está perfeito! Nenhuma compra necessária no momento. 🧶"
        
    mensagem = "🛒 LISTA DE COMPRAS - NAMIGURUMI\n\n"
    
    if em_falta:
        mensagem += "🔴 ESGOTADOS:\n"
        for m in em_falta:
            mensagem += f"- {m.nome} ({m.cor})\n"
        mensagem += "\n"
            
    if acabando:
        mensagem += "🟡 ACABANDO (Só resta 1):\n"
        for m in acabando:
            mensagem += f"- {m.nome} ({m.cor})\n"
            
    return mensagem

def responder_email(para_email, texto_resposta):
    msg = MIMEText(texto_resposta)
    msg['Subject'] = 'Re: Ping Compras - Sua Lista'
    msg['From'] = MEU_EMAIL
    msg['To'] = para_email

    # Conecta ao servidor de envio do Gmail
    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    servidor_smtp.starttls()
    servidor_smtp.login(MEU_EMAIL, MINHA_SENHA)
    servidor_smtp.send_message(msg)
    servidor_smtp.quit()
    print(f"✅ E-mail de resposta enviado para {para_email}!")

def checar_caixa_de_entrada():
    try:
        # Conecta à caixa de entrada do Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(MEU_EMAIL, MINHA_SENHA)
        mail.select('inbox')
        
        # Procura e-mails não lidos com o assunto exato
        status, mensagens = mail.search(None, f'(UNSEEN SUBJECT "{ASSUNTO_GATILHO}")')
        ids_emails = mensagens[0].split()

        for num in ids_emails:
            status, dados_msg = mail.fetch(num, '(RFC822)')
            for resposta in dados_msg:
                if isinstance(resposta, tuple):
                    msg_recebida = email.message_from_bytes(resposta[1])
                    remetente = email.utils.parseaddr(msg_recebida.get('From'))[1]
                    
                    print(f"📧 Ping recebido de {remetente}! Gerando lista...")
                    
                    texto_lista = gerar_texto_lista_compras()
                    responder_email(remetente, texto_lista)
                    
        mail.logout()
    except Exception as e:
        print(f"Erro ao checar e-mail: {e}")

print("🤖 Robô Vigia iniciado! Esperando por e-mails com o assunto 'Ping Compras'...")

# Executa a checagem a cada 60 segundos
while True:
    checar_caixa_de_entrada()
    time.sleep(60)