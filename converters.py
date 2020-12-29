import xml.etree.ElementTree as ET
import copy
from abc import ABC
from utils import parse_numstr, create_numstr, rotate

def convert_common(part: ET.Element):
    """Converts parameters relevant to all parts"""
    part.set('commandPodId', '0')

    position = parse_numstr(part.get('position'))
    position = [2 * x for x in position]
    raw_position = create_numstr(position)
    part.set('position', raw_position)

    materials = part.get('materials')
    part.set('materials', ','.join(materials.split(',')[0:1] * 5))


def convert_fuselage(part: ET.Element):
    """Converts SP Fuselage-Body-1 to SR2 Fuselage1"""
    convert_common(part)
    part.set('partType', 'Fuselage1')

    rotation = parse_numstr(part.get('rotation'))
    rotation = rotate(rotation)
    part.set('rotation', create_numstr(rotation))

    raw_drag = part.get('drag')
    drag = parse_numstr(raw_drag)
    area = [1.5 * x for x in drag]
    raw_area = create_numstr(area)
    part.attrib.pop('drag')
    ET.SubElement(part, 'Drag', {'drag': raw_drag, 'area': raw_area})

    ET.SubElement(part, 'Config')

    tank = part.find('FuelTank.State')
    tank.tag = 'FuelTank'
    tank.attrib.pop('fuel')

    fuselage = part.find('Fuselage.State')
    fuselage.tag = 'Fuselage'

    raw_bottom_scale = fuselage.get('rearScale')
    bottom_scale = parse_numstr(raw_bottom_scale)
    bottom_scale = [x/2 for x in bottom_scale]
    fuselage.set('bottomScale', create_numstr(bottom_scale))

    raw_top_scale = fuselage.get('frontScale')
    top_scale = parse_numstr(raw_top_scale)
    top_scale = [x/2 for x in top_scale]
    fuselage.set('topScale', create_numstr(top_scale))

    corner_tr = [0.0, 0.4, 1.0, 1.0]
    raw_corner_types = fuselage.get('cornerTypes')
    corner_types = parse_numstr(raw_corner_types)
    corner_types = [corner_tr[int(n)] for n in corner_types]
    corner_types[0], corner_types[2] = corner_types[2], corner_types[0]
    corner_types[4], corner_types[6] = corner_types[6], corner_types[4]
    fuselage.set('cornerRadiuses', create_numstr(corner_types))

    offset = parse_numstr(fuselage.get('offset'))
    offset = [x/2 for x in offset]
    offset[1], offset[2] = offset[2], offset[1]
    offset[0] *= -1
    fuselage.set('offset', create_numstr(offset))

    for x in ['version', 'rearScale', 'frontScale', 'buoyancy', 'deadWeight', 'fuelPercentage', 'cornerTypes', 'scale', 'autoSizeOnConnected']:
        fuselage.attrib.pop(x, None)

def convert_wing(part: ET.Element):
    """Converts SP Wing-3 to SR2 Wing1"""
    convert_common(part)
    part.set('partType', 'Wing1')


class PartConverter(ABC):
    def __init__(self, part_type):
        self.partType = part_type
        self.attribs = ['id', 'partType', 'position',
                        'rotation', 'commandPodId', 'materials']

    @staticmethod
    def convert_common(part: ET.Element):
        """Converts parameters relevant to all parts"""
        part.set('commandPodId', '0')

        position = parse_numstr(part.get('position'))
        position = [2 * x for x in position]
        raw_position = create_numstr(position)
        part.set('position', raw_position)

        materials = part.get('materials')
        part.set('materials', ','.join(materials.split(',')[0:1] * 5))

        ET.SubElement(part, 'Config')

    @staticmethod
    def add_drag(part: ET.Element):
        """Adds drag to the part"""
        raw_drag = part.get('drag')
        drag = parse_numstr(raw_drag)
        area = [1.5*x for x in drag]
        raw_area = create_numstr(area)
        ET.SubElement(part, 'Drag', {'drag': raw_drag, 'area': raw_area})

    def convert_specific(self, part: ET.Element):
        """Converts parameters specific to the part"""
        pass

    def pop_attribs(self, part: ET.Element):
        """Pops unnecessary attribs of the part"""
        part.attrib = {x: part.attrib[x] for x in part.attrib if x in self.attribs}

    def convert(self, part: ET.Element):
        """Converts the part from SP to SR2"""
        self.convert_common(part)
        part.set('partType', self.partType)
        self.add_drag(part)
        self.convert_specific(part)
        self.pop_attribs(part)


class FuselageConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Fuselage1')

    def convert_specific(self, part: ET.Element):
        rotation = parse_numstr(part.get('rotation'))
        rotation = rotate(rotation)
        part.set('rotation', create_numstr(rotation))

        tank = part.find('FuelTank.State')
        tank.tag = 'FuelTank'
        tank.attrib.pop('fuel')

        fuselage = part.find('Fuselage.State')
        fuselage.tag = 'Fuselage'

        raw_bottom_scale = fuselage.get('rearScale')
        bottom_scale = parse_numstr(raw_bottom_scale)
        bottom_scale = [x/2 for x in bottom_scale]
        fuselage.set('bottomScale', create_numstr(bottom_scale))

        raw_top_scale = fuselage.get('frontScale')
        top_scale = parse_numstr(raw_top_scale)
        top_scale = [x/2 for x in top_scale]
        fuselage.set('topScale', create_numstr(top_scale))

        corner_tr = [0.0, 0.4, 1.0, 1.0]
        raw_corner_types = fuselage.get('cornerTypes')
        corner_types = parse_numstr(raw_corner_types)
        corner_types = [corner_tr[int(n)] for n in corner_types]
        corner_types[0], corner_types[2] = corner_types[2], corner_types[0]
        corner_types[4], corner_types[6] = corner_types[6], corner_types[4]
        fuselage.set('cornerRadiuses', create_numstr(corner_types))

        offset = parse_numstr(fuselage.get('offset'))
        offset = [x/2 for x in offset]
        offset[1], offset[2] = offset[2], offset[1]
        offset[0] *= -1
        fuselage.set('offset', create_numstr(offset))

        for x in ['version', 'rearScale', 'frontScale',
                  'buoyancy', 'deadWeight', 'fuelPercentage',
                  'cornerTypes', 'scale', 'autoSizeOnConnected']:
            fuselage.attrib.pop(x, None)

class WingConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Wing1')

    def convert_specific(self, part: ET.Element):
        tank = part.find('FuelTank.State')
        part.remove(tank)

        wing = part.find('Wing.State')
        wing.tag = 'Wing'
        wing_inverted = wing.get('inverted', 'false') == 'true'

        for attrib_name in ('rootLeadingOffset', 'rootTrailingOffset',
                            'tipLeadingOffset', 'tipPosition', 'tipTrailingOffset'):
            raw_attrib = wing.get(attrib_name)
            attrib_val = parse_numstr(raw_attrib)
            attrib_val = [x*2 for x in attrib_val]
            wing.set(attrib_name, create_numstr(attrib_val))

        control_surfaces = wing.findall('ControlSurface')
        for surface in control_surfaces:
            inp = surface.get('inputId')
            surface.set('input', inp)
            surface.attrib.pop('inputId', None)
            if wing_inverted:
                surface_inverted = surface.get('invert', 'false') == 'true'
                surface.set('invert', str(not surface_inverted).casefold())
            for attrib_name in ('start', 'end'):
                raw_attrib = surface.get(attrib_name)
                attrib_val = parse_numstr(raw_attrib)
                attrib_val = [int(x*2) for x in attrib_val]
                surface.set(attrib_name, create_numstr(attrib_val))
            wing.remove(surface)
        part.extend(control_surfaces)
