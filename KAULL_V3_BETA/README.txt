KAULL PUBLIC TEST

LOCAL
1. Execute START.bat
2. Abra http://127.0.0.1:8080

RENDER
Build command: pip install -r requirements.txt
Start command: python server.py
Health check: /health

O servidor usa automaticamente a variavel PORT fornecida pelo host.
Em HTTPS, o frontend troca automaticamente ws:// por wss://.

FREE
- Ate 3 pessoas por sala
- Ate 720p
- Tela + audio fornecido pelo compartilhamento do navegador
- Slots preparados para anuncios

OBS: esta versao ainda usa STUN publico e nao possui TURN. Em algumas redes/NATs, a transmissao WebRTC pode nao conectar. Para producao, configure TURN.
