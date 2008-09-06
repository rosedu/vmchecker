#! /usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi, brtzsnr@gmail.com'

import optparse



cmdline = optparse.OptionParser(version='%prog 0.1')
cmdline.add_option('--homework', type='string', dest='homework',
                   help='fișierul de configurare a temei')
cmdline.add_option('--ip', type='string', dest='ip',
                   help='adresa IP a sistemului de testare')
cmdline.add_option('--path', type='string', dest='path',
                   help='calea de stocare la distanta a fisierelor')

def main():
    options = cmdline.parse_args()[0]



if __name__ == '__main__':
    main()
