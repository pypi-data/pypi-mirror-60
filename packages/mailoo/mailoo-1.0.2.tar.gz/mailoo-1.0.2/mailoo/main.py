from mailoo import Mail


print('##########################################')
print('##########################################')
print('##########################################')
print('################# MAILOO #################')
print('########## by Wellington Gadelha #########')
print('##########################################')
print('##########################################')

USER_EMAIL = input('Digite o seu email: ')
EMAIL_DEST = input('Digite os emails dos destinatarios: ')
SUBJECT = input('Assunto: ')
PASS = input('Digite a senha: ')
USER_PASS_GMAIL = 'ohxadhlbmzlvqkim'
while True:
    print()
    print('---CONTEUDO DO EMAIL---')
    print('1 -> ESCREVER MENSAGEM')
    print('2 -> ENVIAR ARQUIVO HTML')
    print()
    OP_MESSAGE = input('Digite a Opção desejada: ').strip()
    print()
    if OP_MESSAGE == '1':
        msg = input('Digite sua Mensagem: ')
        email = Mail(USER_EMAIL,PASS)
        email.send(SUBJECT, msg,file_emails=EMAIL_DEST)
    elif OP_MESSAGE == '2':
        msg = input('Digite o nome do Arquivo: ')
        email = Mail(USER_EMAIL,PASS)
        email.send(SUBJECT,file_html=msg,file_emails=EMAIL_DEST)
    else:
        print('Opçao Invalida.')
    break

