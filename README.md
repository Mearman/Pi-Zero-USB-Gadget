# Pi-Zero-USB-Gadget
A hacked together guide for working WiFi USB storage on the [Pi Zero W](https://amzn.to/2U75sE1)

Initially I started with the MagPi magazine's solution from [here](https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive) and the watchdog script from [here](http://rpf.io/usbzw).

USB mass storage mode is accessible by the OTG port on the Pi Zero or via a USB-A expansion board like [this](https://amzn.to/2yIc0lc) one that I use.

# Setup process

## Initial config

1. Flash your Raspbian lite version of choice. (I have been using this with Buster lite)
2. Add an empty file named `ssh` file and appropriately populated wpa_supplicant.conf file into the boot partition
3. Boot up the system, ssh in, and perform the customary `sudo apt-get update` and `sudo apt-get upgrade`

## USB Gadget setup

3. Add `dtoverlay=dwc2` to the bottom of `/boot/config.txt`
4. Add `dwc2` to the end of `/etc/modules`
5. Reboot the system
6. Create the storage file with:
   - `sudo dd bs=1M if=/dev/zero of=/piusb.bin count=2048`
   - `mkdosfs /piusb.bin -F 32 -I`
7. Mount the storage file with
   - Create the mountpoint: `sudo mkdir /mnt/usb_share`
   - Add `/piusb.bin /mnt/usb_share vfat users,umask=000 0 2` to your `/etc/fstab`
   - Test with `sudo mount -a`
8. Test your USB accessibility with `sudo modprobe g_mass_storage file=/piusb.bin stall=0 removable=y`

## Samba access

9. Make sure you're up-to-date with: `sudo apt-get update` and and install samba `sudo apt-get install samba winbind -y`
10. Creat the samba share in `/etc/samba/smb.conf`

```
[usb]
browseable = yes
path = /mnt/usb_share
guest ok = yes
read only = no
create mask = 777
```

11. Don't forget to change your Pi's hostname in `/etc/hostname` and `/etc/hosts`

## Setting up the watchdog script

12. Install python watchdog with: `sudo pip3 install watchdog`
13. Download and move the `usb_share.py` to somewhere sensible like `/usr/local/share`
14. Make it executable with `sudo chmod +x usbshare.py`
15. Automatically running watchdog
    - At this point, the original guide created a service. I would still rather use a service so please feel free to fork, add it it and make a pull-request
    - Instead, simply run the watchdog script at startup by adding it to the sudoers crontab by running `sudo crontab -e` and adding `@reboot sudo python3 /usr/local/share/usb_share.py`

---

For reference, the original service was as follows:

```
[Unit]
Description=USB Share Watchdog

[Service]
Type=simple
ExecStart=/usr/local/share/usb_share.py
Restart=always

[Install]
WantedBy=multi-user.target
```
