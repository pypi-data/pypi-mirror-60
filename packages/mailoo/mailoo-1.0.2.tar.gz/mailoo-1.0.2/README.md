# Mailoo
![OpenSource](https://img.shields.io/static/v1?label=GitHub&message=Opensource&color=blue&logo=github&logoColor=violet)
![BuildPassing](https://img.shields.io/static/v1?label=build&message=passing&color=brightgreen)
![PythonVersion](https://img.shields.io/static/v1?label=python&message=>=3.6&color=brightgreen&logo=python&logoColor=white)
[![Pypi](https://img.shields.io/static/v1?label=Pypi&logo=pypi&logoColor=white&message=v1.0.2&color=9f55ff)](https://pypi.org/project/mailoo/)

[![HitCount](https://hits.dwyl.com/informeai/mailoo.svg)](http://hits.dwyl.com/informeai/mailoo)

Modulo Python que facilita o envio de Emails  usando  provedores `SMTP`. 

Com funçoes de carregamento de conteudo de arquivos, à escritas de `html` in-line. 

O mesmo proporciona de forma facil e com poucas linhas a criaçao e envio de emails.

Para os amantes de `Email-Marketing` ou Entusiastas em geral.

Suporte para Versao 3 de Python

### Instalaçao:
```
 $ pip install mailoo
```

### Uso
```
>> import mailoo

>> email = mailoo.Mail(email_user, key_pass)   # email_user -> email do usuário.

                                               # key_pass -> Chave de Aplicativo 
                                               -> GMAIL, ou senha do email nos 
                                               demais casos.

>> email.send(subject,msg,email)               # Envio do email...
```
### Outros Usos
```
============
Emails.txt:
|-- email1
|-- email2
|-- ...
============

>> email.send(subject,msg, Emails.txt)

######### OU #########
                                            
>> email.send(subject,file.html, arquivo.txt)  # arquivo html para varios emails.

                                               # file.html -> arquivo html a ser 
                                               enviado no lugar de uma mensagem 
                                               comum.

```

## Características
* Envio de Varios emails com simplicidade.

* Escolha automática de envio via SSL/TLS.

* Escreva mensagens simples ou insira texto html.

* Leitura e envio de conteudo de arquivo html/txt.

### Obs:
```
O modulo usa os servidores de saída dos provedores de emails do usuário.
EX: GMAIL, OUTLOOK, HOTMAIL,YAHOO.

Portanto Cuidado com os Limites estabelecidos por esses provedores, pois os
mesmos estabelecem políticas de controle de envio. No geral os mesmos possuem
limites MÁXIMOS DE ENVIO de 300 emails/dia.
Observando e Respeitando os limites estabelecidos, usem o modulo a vontade...
```
## Contato:
@informeai

[![Facebook](https://img.shields.io/static/v1?label=facebook&style=social&logo=Facebook&message=page)](https://www.facebook.com/informeai/)
[![Instagram](https://img.shields.io/static/v1?label=instagram&style=social&logo=Instagram&message=perfil)](https://www.instagram.com/informeaioficial/)
[![Twitter](https://img.shields.io/static/v1?label=twitter&style=social&logo=Twitter&message=desenvolvedor)](https://twitter.com/WellingtonGade4)