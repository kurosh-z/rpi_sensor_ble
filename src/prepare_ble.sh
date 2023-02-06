

sudo rm -r /var/lib/bluetooth       
 sudo systemctl daemon-reload     
sudo systemctl stop bluetooth.service 
sudo systemctl start bluetooth.service   
sudo systemctl status bluetooth.service    