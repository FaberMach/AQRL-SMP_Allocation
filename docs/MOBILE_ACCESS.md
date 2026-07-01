# Acesso Mobile

O dashboard esta servido localmente na porta 8000.

## Endereco atual

Na rede Wi-Fi atual, a maquina respondeu em:

```text
http://192.168.15.22:8000
```

Abra esse endereco no navegador do celular enquanto ele estiver na mesma rede Wi-Fi.

## Se nao abrir

1. Confirme que o servidor esta rodando:

   ```powershell
   py -m http.server 8000 -d dashboard
   ```

2. Descubra o IP Wi-Fi atual:

   ```powershell
   Get-NetIPAddress -AddressFamily IPv4
   ```

3. Teste no desktop:

   ```powershell
   Invoke-WebRequest -Uri http://localhost:8000 -UseBasicParsing
   ```

4. Se o desktop abre mas o celular nao, o bloqueio mais provavel e firewall do Windows para conexoes de entrada na porta 8000.

