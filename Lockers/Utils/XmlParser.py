__author__ = 'mgradob'

""" Imports """
import xml.etree.ElementTree as Xmlet


class XmlParser:
    """
    XmlParser Class.
     Manages all xml related data.
    """

    def split_sting(self, data):
        """
        Split_string method.
         Removes trailing data of the xml string, up until tag '<?xml... ?>'
        """
        index = data.find('<?')
        xml = data[index:]
        return xml

    def get_rom_code(self, data):
        """
        Get_rom_code method.
         Returns the rom_code (key) of the credential.
        """
        xml = self.split_sting(data)
        tree = Xmlet.fromstring(xml)
        rom_code = tree[1][0].text
        return rom_code

    def __init__(self):
        pass