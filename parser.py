import requests
import xml.etree.ElementTree as ET

SPB_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_SPB.yml'
MSK_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_MSK.yml'
OUTPUT = 'catalog.yml'


def load_xml(url):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return ET.fromstring(r.content)


def clean_tag(tag):
    return tag.split('}')[-1]


def find_offers(root):
    offers = {}
    for elem in root.iter():
        if clean_tag(elem.tag) == 'offer' and elem.attrib.get('id'):
            offers[elem.attrib['id']] = elem
    return offers


def find_param(offer, name):
    for elem in offer.iter():
        if clean_tag(elem.tag) == 'param' and elem.attrib.get('name') == name:
            return elem
    return None


def get_stock(offer):
    if offer is None:
        return '0'
    for elem in offer.iter():
        if clean_tag(elem.tag) == 'stock':
            return elem.text or '0'
    param = find_param(offer, 'Остаток')
    return param.text if param is not None and param.text else '0'


spb_root = load_xml(SPB_URL)
msk_root = load_xml(MSK_URL)

spb_offers = find_offers(spb_root)
msk_offers = find_offers(msk_root)

if len(spb_offers) == 0:
    raise Exception('SPB offers not found')

for offer_id, offer in spb_offers.items():
    spb = get_stock(offer)
    msk = get_stock(msk_offers.get(offer_id))

    p_spb = find_param(offer, 'Остаток СПБ')
    if p_spb is None:
        p_spb = ET.SubElement(offer, 'param', {'name': 'Остаток СПБ'})
    p_spb.text = spb

    p_msk = find_param(offer, 'Остаток МСК')
    if p_msk is None:
        p_msk = ET.SubElement(offer, 'param', {'name': 'Остаток МСК'})
    p_msk.text = msk

ET.ElementTree(spb_root).write(OUTPUT, encoding='utf-8', xml_declaration=True)

print(f'SPB offers: {len(spb_offers)}')
print(f'MSK offers: {len(msk_offers)}')
print('Catalog generated successfully')
