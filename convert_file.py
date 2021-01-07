import xml.etree.ElementTree as ET
import uuid
import io
from typing import BinaryIO
from utils import parse_numstr, create_numstr
from part_converters import FuselageConverter, WingConverter, NoseConeConverter, InletConverter
from command_pod import command_pod


CONVERTERS = {'Fuselage-Body-1': FuselageConverter(),
              'Wing-3': WingConverter(),
              'Fuselage-Cone-1': NoseConeConverter(),
              'Fuselage-Inlet-1': InletConverter()}
CONVERTERS['Wing-2'] = CONVERTERS['Wing-3']

def convert_craft(craft: ET.Element):
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
    ET.SubElement(craft, 'Symmetry')

def convert_parts(assembly: ET.Element, scale) -> set:
    parts = assembly.find('Parts')
    part_ids = set()
    for part in list(parts):
        if part.get('partType') in CONVERTERS:
            part_ids.add(part.get('id'))
            converter = CONVERTERS[part.get('partType')]
            converter.convert(part, scale)
        else:
            parts.remove(part)
    parts.insert(0, command_pod)
    return part_ids

def convert_connections(assembly: ET.Element, part_ids: set):
    connections = assembly.find('Connections')
    for conn in list(connections):
        a = conn.get('partA')
        b = conn.get('partB')
        if a not in part_ids or b not in part_ids:
            connections.remove(conn)

def convert_bodies(assembly: ET.Element, part_ids: set):
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

def convert_theme(craft: ET.Element):
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

def convert_file(source: BinaryIO, scale=1) -> BinaryIO:
    tree = ET.parse(source)
    craft = tree.getroot()
    convert_craft(craft)

    assembly = craft.find('Assembly')

    part_ids = convert_parts(assembly, scale)
    convert_connections(assembly, part_ids)
    convert_bodies(assembly, part_ids)
    convert_theme(craft)

    output = io.BytesIO()
    tree.write(output, encoding='utf-8', xml_declaration=True)
    output.seek(0)
    return output
