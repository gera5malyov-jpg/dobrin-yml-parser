import requests
import xml.etree.ElementTree as ET

SPB_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_SPB.yml'
MSK_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_MSK.yml'
OUTPUT = 'catalog.yml'


def load_xml(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    text = r.content
    return ET.fromstring(text)


def find_offers(root):
    result = {}
    for elem in root.iter():
        if elem.tag.endswith('offer') and elem.attrib.get('id'):
            result[elem.attrib['id']] = elem
    return result


def get_stock(offer):
    if offer is None:
        return '0'
    for child in offer.iter():
        if child.tag.endswith('stock'):
            return child.text or '0'
    for child in offer.findall('.//param'):
        if child.attrib.get('name') == 'Остаток':
            return child.text or '0'
    return '0'


spb_root = load_xml(SPB_URL)
msk_root = load_xml(MSK_URL)

msk_offers = find_offers(msk_root)
spb_offers = find_offers(spb_root)

count = 0
for offer_id, offer in spb_offers.items():
    spb_stock = get_stock(offer)
    msk_stock = get_stock(msk_offers.get(offer_id))

    existing = {p.attrib.get('name'): p for p in offer.findall('param')}

    p = existing.get('Остаток СПБ')
    if p is None:
        p = ET.SubElement(offer, 'param', {'name': 'Остаток СПБ'})
    p.text = spb_stock

    p = existing.get('Остаток МСК')
    if p is None:
        p = ET.SubElement(offer, 'param', {'name': 'Остаток МСК'})
    p.text = msk_stock

    count += 1

ET.ElementTree(spb_root).write(OUTPUT, encoding='utf-8', xml_declaration=True)
print(f'Generated {count} offers')
