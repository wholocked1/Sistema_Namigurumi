import os
import time
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from database import DatabaseCSV
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# ==========================================
# CONFIGURAÇÕES DO SEU E-MAIL (SEGURAS)
# ==========================================
MEU_EMAIL = os.getenv("EMAIL_BOT")  
MINHA_SENHA = os.getenv("SENHA_BOT")

# Validação de segurança para garantir que o arquivo .env foi lido com sucesso
if not MEU_EMAIL or not MINHA_SENHA:
    print("\n❌ ERRO CRÍTICO: O robô não conseguiu ler o arquivo .env!")
    print("Verifique se o arquivo .env existe na raiz do projeto e se contém as variáveis certas.\n")
    exit()

ASSUNTO_GATILHO = "Ping Compras"
EMAILS_RESPONDIDOS = set()

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

    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    servidor_smtp.starttls()
    servidor_smtp.login(MEU_EMAIL, MINHA_SENHA)
    servidor_smtp.send_message(msg)
    servidor_smtp.quit()
    print(f"✅ E-mail de resposta enviado para {para_email}!")

def checar_caixa_de_entrada():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(MEU_EMAIL, MINHA_SENHA)
        mail.select('inbox')
        
        status, mensagens = mail.uid('search', None, f'(UNSEEN SUBJECT "{ASSUNTO_GATILHO}")')
        uids_emails = mensagens[0].split()

        for uid in uids_emails:
            status, dados_msg = mail.uid('fetch', uid, '(RFC822)')
            for resposta in dados_msg:
                if isinstance(resposta, tuple):
                    msg_recebida = email.message_from_bytes(resposta[1])
                    
                    # --------------------------------------------------------
                    # FILTRO DE SEGURANÇA CONTRA DUPLICIDADE DE ASSUNTO
                    # --------------------------------------------------------
                    assunto = msg_recebida.get('Subject', '')
                    assunto_limpo = assunto.strip().lower()
                    
                    # Se conter "re:" ou não for EXATAMENTE o gatilho, ignora
                    if "re:" in assunto_limpo or assunto_limpo != ASSUNTO_GATILHO.lower():
                        mail.uid('store', uid, '+FLAGS', '\\Seen') # Marca como lido para sumir do radar
                        continue
                    
                    msg_id = msg_recebida.get('Message-ID')
                    if msg_id in EMAILS_RESPONDIDOS:
                        continue
                        
                    remetente = email.utils.parseaddr(msg_recebida.get('From'))[1]
                    
                    print(f"📧 Ping legítimo recebido de {remetente}! Gerando lista...")
                    
                    texto_lista = gerar_texto_lista_compras()
                    responder_email(remetente, texto_lista)
                    
                    EMAILS_RESPONDIDOS.add(msg_id)
                    
                    # Marca como lido e deleta o ping original do usuário para limpar a caixa
                    mail.uid('store', uid, '+FLAGS', '\\Seen')
                    mail.uid('store', uid, '+FLAGS', '\\Deleted')
                    
        mail.expunge()
        mail.logout()
    except Exception as e:
        print(f"Erro ao checar e-mail: {e}")

print("🤖 Robô Vigia iniciado! Esperando por e-mails com o assunto 'Ping Compras'...")

while True:
    checar_caixa_de_entrada()
    time.sleep(60)