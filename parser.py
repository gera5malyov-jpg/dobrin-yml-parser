import requests
import xml.etree.ElementTree as ET

SPB_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_SPB.yml'
MSK_URL = 'https://partner.d-o-b-r-i-n.com/YML/DOBRIN_YML_MSK.yml'
OUTPUT = 'catalog.yml'


def load_xml(url):
    r = requests.get(url, timeout=120, headers={'User-Agent': 'Mozilla/5.0'})
    r.raise_for_status()
    return ET.fromstring(r.content)


def tag(e):
    return e.tag.split('}')[-1]


def find_offers(root):
    return {e.attrib['id']: e for e in root.iter() if tag(e) == 'offer' and 'id' in e.attrib}


def find_shop_offers(root):
    for e in root.iter():
        if tag(e) == 'offers':
            return e
    return None


def find_param(offer, name):
    for e in offer.iter():
        if tag(e) == 'param' and e.attrib.get('name') == name:
            return e
    return None


def stock(offer):
    if offer is None:
        return '0'
    for e in offer.iter():
        if tag(e) in ('stock', 'quantity', 'available'):
            return e.text or '0'
    p = find_param(offer, 'Остаток')
    return p.text if p is not None else '0'


spb_root = load_xml(SPB_URL)
msk_root = load_xml(MSK_URL)

spb_offers = find_offers(spb_root)
msk_offers = find_offers(msk_root)

print('SPB offers:', len(spb_offers))
print('MSK offers:', len(msk_offers))

if not spb_offers:
    raise Exception('No SPB offers found')

changed = 0
for oid, offer in spb_offers.items():
    for name, value in [('Остаток СПБ', stock(offer)), ('Остаток МСК', stock(msk_offers.get(oid)))]:
        p = find_param(offer, name)
        if p is None:
            p = ET.SubElement(offer, 'param', {'name': name})
        p.text = value
    changed += 1

if changed == 0:
    raise Exception('No offers generated')

ET.ElementTree(spb_root).write(OUTPUT, encoding='utf-8', xml_declaration=True)

size = __import__('os').path.getsize(OUTPUT)
print('Generated offers:', changed)
print('Catalog size:', size, 'bytes')

if size < 1000:
    raise Exception('Catalog file is too small')
