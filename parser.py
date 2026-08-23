import requests
import xml.etree.ElementTree as ET

SPB_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_SPB.yml'
MSK_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_MSK.yml'
OUTPUT = 'catalog.yml'


def load_xml(url):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return ET.fromstring(response.content)


def get_offers(root):
    return {offer.attrib.get('id'): offer for offer in root.findall('.//offer')}


spb_root = load_xml(SPB_URL)
msk_root = load_xml(MSK_URL)

msk_offers = get_offers(msk_root)

for offer in spb_root.findall('.//offer'):
    offer_id = offer.attrib.get('id')
    msk_offer = msk_offers.get(offer_id)

    spb_stock = offer.find('stock')
    msk_stock = msk_offer.find('stock') if msk_offer is not None else None

    params = {p.attrib.get('name'): p for p in offer.findall('param')}

    p_spb = params.get('Остаток СПБ')
    if p_spb is None:
        p_spb = ET.SubElement(offer, 'param', {'name': 'Остаток СПБ'})
    p_spb.text = spb_stock.text if spb_stock is not None else '0'

    p_msk = params.get('Остаток МСК')
    if p_msk is None:
        p_msk = ET.SubElement(offer, 'param', {'name': 'Остаток МСК'})
    p_msk.text = msk_stock.text if msk_stock is not None else '0'

ET.ElementTree(spb_root).write(OUTPUT, encoding='utf-8', xml_declaration=True)
