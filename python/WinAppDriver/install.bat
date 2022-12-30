netsh advfirewall firewall delete rule name=WinAppDriver
netsh advfirewall firewall add rule name=WinAppDriver dir=in action=allow protocol=tcp localport=4723
