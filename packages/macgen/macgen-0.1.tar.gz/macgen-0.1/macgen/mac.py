# Generate a MAC address according to the EUI-48 format
# https://en.wikipedia.org/wiki/MAC_address
#
# 6 octets
#   -or-
# 3 octets (OUI), 3 octets (NIC)
#
#   - OUI = Organisationally Unique Identifier
#   - NIC = Network Interface Controller
#
# the first octet has two flags:
#   - b0 = 0: unicast         / 1: multicast
#   - b1 = 0: globally unique / 1: locally administered

from os import urandom

class MacGen:
    def __init__(self, oui=None):
        self.oui = oui

    def generate_random(self, octet_count):
        return [ _ for _ in urandom(octet_count) ]

    def generate(self, oui=None, is_multicast=False, is_local=True):
        if oui is None:
            oui = self.oui

        if oui is not None:
            oui_bytes = [ _ for _ in oui ]
            mac_bytes = [ *oui_bytes[:3], self.generate_random(3) ]

        else:
            mac_bytes = self.generate_random(6)

            if is_multicast:
                mac_bytes[0] |=  0x01
            else:
                mac_bytes[0] &= ~0x01

            if is_local:
                mac_bytes[0] |=  0x02
            else:
                mac_bytes[0] &= ~0x02

        return mac_bytes

    def generate_text(self, sep=':', oui=None, is_multicast=False, is_local=True):
        mac_bytes = self.generate(oui, is_multicast, is_local)

        return sep.join([ f'{_:02X}' for _ in mac_bytes ])
