from smtplib import SMTP_SSL, SMTP, SMTPAuthenticationError,SMTPException,SMTPHeloError,SMTPResponseException,SMTPServerDisconnected
from email.message import EmailMessage
from email.mime.text import MIMEText


class Mail:
    """
    Classe em Python para criaçao de Emails e envios via servidores SMTPs...
    Uso da Classe:
    Se o Email do Usuário for do GMAIL -> Necessario criar chave de aplicativo , Link: https://support.google.com/mail/answer/185833?hl=pt-BR, 
    de posse da chave , usar como a senha.
    Se o Email do Usuário for do OUTLOOK,HOTMAIL,YAHOO -> Usar email e senha padrao.

    """

    def __init__(self,user_email:str, key_acess:str):
        """
        Metodo de Inicializaçao do Objeto Email...
        Cria uma instancia do Objeto Mail.
        """
        self.user_email = user_email
        self.key_acess = key_acess
        self.host, self.port = self._provider(self.user_email)
        return

    def send(self,subject:str,msg:str=None,email:str=None,file_html:str=None,file_emails:str=None):
        """
        Método responsavel por enviar emails...
        USO: 
        msg ou file_html -> mensagem a ser enviada/arquivo html a ser enviado.
        email ou file_emails -> email unico de destinatário/arquivo 'TXT', contendo emails.
        subject -> Assunto do Email.

        """
        if msg and file_html or email and file_emails:
            print(f'Duplicidade de Argumentos : USO -> msg ou file_html, emails ou file_emails')
        else:

            if not msg and not file_html:
                print(f'Escreva uma mensagem ou envie um arquivo html.')

            if file_emails and msg:
                list_emails_msg = self._load_emails(file_emails)
                for email in list_emails_msg:
                    self._send_text(msg,subject,email)
            elif msg and email:
                self._send_text(msg,subject,email)
            elif file_emails and file_html:
                list_emails_html = self._load_emails(file_emails)
                for email in list_emails_html:
                    self._send_file(file_html,subject,email)
            else:
                self._send_file(file_html,subject,email)
            
        

    def _send_file(self, file, subject:str,dest_email:str):
        """
        Metodo Usado para envio de Arquivos. Ex: *.html, *.txt.
        """
        self.file = file
        
        try:
            with open(self.file,'rb') as arquivo:
                content_html = arquivo.read()
                arquivo.close()
        except FileNotFoundError:
            print(f'ARQUIVO: \033[1;91m{self.file}\033[0;0m não Existe.\n')
        else:
            print(f'Arquivo Lido com Sucesso.\n')
            

        self.msg = content_html
        self.subject = subject
        self.dest_email = dest_email
        self.msg = self._html(self.msg, self.dest_email,subject=self.subject)
        
        if self.host == 'smtp.office365.com':
            try:
                with  SMTP(self.host, self.port) as mail_noSSl:
                    mail_noSSl.starttls()
                    mail_noSSl.login(self.user_email, self.key_acess)
                    mail_noSSl.send_message(self.msg, self.user_email, self.dest_email)
                    mail_noSSl.quit()
            except Exception as err:
                print(f'ERROR: {err}')
            else:
                print(f'Email enviado ao DESTINATARIO: \033[1;32m{self.dest_email}\033[0;0m  concluido.')
        else:
            with SMTP_SSL(self.host, self.port) as mail:
                try:
                    mail.login(self.user_email,self.key_acess)
                except SMTPAuthenticationError:
                    print(f'O Servidor não aceitou a combinação do USUÁRIO: {self.user_email} , mais a SENHA')
                except SMTPHeloError:
                    print(f'O Servidor de Email não respondeu a solicitação de login.')
                except SMTPServerDisconnected:
                    print(f'O Servidor Desconectou Inesperadamente.')
                except SMTPResponseException as resp_err:
                    print(f'Houve um erro com a resposta do servidor.\n CODE: {resp_err.smtp_code}.\n ERROR: {resp_err.smtp_error}')
                except SMTPException:
                    print(f'Nenhum método de Authenticação encontrado.')
                
                try:
                    mail.send_message(self.msg,self.user_email,self.dest_email)
                    mail.quit()
                except Exception as err:
                    print(err)
                else:
                    print(f'Email enviado ao DESTINATARIO: \033[1;32m{self.dest_email}\033[0;0m concluido')

    def _send_text(self, text, subject:str,dest_email:str):
        """
        Metodo Usado para envio de Texto simple ou html in-line.
        """
        self.msg = text
        self.subject = subject
        self.dest_email = dest_email
        
            
        self.msg = self._html(self.msg, self.dest_email,subject=self.subject)


        if self.host == 'smtp.office365.com':
            try:
                with SMTP(self.host, self.port) as mail_noSSl:
                    mail_noSSl.starttls()
                    mail_noSSl.login(self.user_email, self.key_acess)
                    mail_noSSl.send_message(self.msg, self.user_email, self.dest_email)
                    mail_noSSl.quit()
            except Exception as err:
                print(f'ERROR: {err}')
            else:
                print(f'Email enviado ao DESTINATARIO: \033[1;32m{self.dest_email}\033[0;0m  concluido.')
        else:
            with SMTP_SSL(self.host, self.port) as mail:
                try:
                    mail.login(self.user_email,self.key_acess)
                except SMTPAuthenticationError:
                    print(f'O Servidor não aceitou a combinação do USUÁRIO: {self.user_email} , mais a SENHA')
                except SMTPHeloError:
                    print(f'O Servidor de Email não respondeu a solicitação de login.')
                except SMTPServerDisconnected:
                    print(f'O Servidor Desconectou Inesperadamente.')
                except SMTPResponseException as resp_err:
                    print(f'Houve um erro com a resposta do servidor.\n CODE: {resp_err.smtp_code}.\n ERROR: {resp_err.smtp_error}')
                except SMTPException:
                    print(f'Nenhum método de Authenticação encontrado.')
                    
                try:
                    mail.send_message(self.msg,self.user_email,self.dest_email)
                    mail.quit()
                except Exception as err:
                    print(err)
                else:
                    print(f'Email enviado ao DESTINATARIO: \033[1;32m{self.dest_email}\033[0;0m concluido')

    def _html(self, msg, dest_email,subject=None):
        self.msg = msg
        self.subject = subject
        self.dest_email = dest_email
        self.obj_email = EmailMessage()
        self.obj_email['Subject'] = self.subject
        self.obj_email['From'] = self.user_email
        self.obj_email['To'] = self.dest_email
        self.obj_email.set_type('text/html', header='Content-Type', requote=False)
        self.obj_email.set_payload(self.msg,charset='utf-8')
        
        return self.obj_email
        

    def _provider(self, user:str):
        if "@gmail" in user:
            return ('smtp.gmail.com', 465)
        elif "@outlook" in user or "@hotmail" in user:
            return ('smtp.office365.com', 587)
        elif "@yahoo" in user:
            return ('smtp.mail.yahoo.com', 465)
        
            
    def _load_emails(self,file:str) -> list:
        lista_emails = []
        try:
            with open(file, 'rt') as arq_emails:
                emails = arq_emails.readlines()
                for email in emails:
                    if '\n' in email:
                        email = email[:-1]
                    lista_emails.append(email)
            arq_emails.close()
        except FileNotFoundError:
            print(f'Arquivo:  \033[1;91m{file}\033[0;0m nao reconhecido')
        else:
            print(f'Lista de Arquivos de Emails Carregado.')
            return lista_emails
        
