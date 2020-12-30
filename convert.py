import xml.etree.ElementTree as ET
import uuid
from utils import parse_numstr, create_numstr
from converters import FuselageConverter, WingConverter, NoseConeConverter, InletConverter
from command_pod import command_pod

SCALE = 1

INPUT_PATH = '/Users/pasha/projects/SP-SR2-converter/test_crafts/BL-13.N11.1.1.xml'
OUTPUT_PATH = './test_results/test71.xml'

tree = ET.parse(INPUT_PATH)
craft = tree.getroot()
craft.tag = 'Craft'
craft.attrib.pop('url')
craft.attrib.pop('theme')
craft.set('xmlVersion', '5')
craft.set('parent', '')
craft.set('price', '314159')

raw_boundsmin = craft.get('boundsMin')
raw_size = craft.get('size')
craft.set('initialBoundsMin', raw_boundsmin)
craft.attrib.pop('boundsMin')
craft.attrib.pop('size')

boundsmin = parse_numstr(raw_boundsmin)
size = parse_numstr(raw_size)
boundsmax = [a+b for a, b in zip(boundsmin, size)]
raw_boundsmax = create_numstr(boundsmax)
craft.set('initialBoundsMax', raw_boundsmax)


assembly = craft.find('Assembly')
parts = assembly.find('Parts')

converters = {'Fuselage-Body-1': FuselageConverter(scale=SCALE),
              'Wing-3': WingConverter(scale=SCALE),
              'Fuselage-Cone-1': NoseConeConverter(scale=SCALE),
              'Fuselage-Inlet-1': InletConverter(scale=SCALE)}
converters['Wing-2'] = converters['Wing-3']

part_ids = set()
for part in list(parts):
    if part.get('partType') not in converters:
        parts.remove(part)
        continue

    part_ids.add(part.get('id'))
    converter = converters[part.get('partType')]
    converter.convert(part)

parts.insert(0, command_pod)

connections = assembly.find('Connections')
for conn in list(connections):
    a = conn.get('partA')
    b = conn.get('partB')
    if a not in part_ids or b not in part_ids:
        connections.remove(conn)

bodies = assembly.find('Bodies')
n = 1
for body in list(bodies):
    raw_body_part_ids = body.get('partIds')
    body_part_ids = raw_body_part_ids.split(',')
    body_part_ids = [x for x in body_part_ids if x in part_ids]
    if not body_part_ids:
        bodies.remove(body)
        continue
    raw_body_part_ids = ','.join(body_part_ids)
    body.set('partIds', raw_body_part_ids)

    body.set('id', str(n))
    body.set('mass', '3.14159265')
    body.set('centerOfMass', '0,0,0')
    body.attrib.pop('angularVelocity')
    body.attrib.pop('velocity')

    n += 1

theme = craft.find('Theme')
theme_name = theme.get('name')
theme_id = str(uuid.uuid1())
theme.set('id', theme_id)
for color in theme:
    color.attrib.pop('r', None)
craft.remove(theme)

designer_settings = ET.SubElement(
    craft, 'DesignerSettings', {'themeName': theme_name})
designer_settings.append(theme)

themes = ET.SubElement(craft, 'Themes')
themes.append(theme)

ET.SubElement(craft, 'Symmetry')
tree.write(OUTPUT_PATH, encoding='utf-8', xml_declaration=True)
