import xml.etree.ElementTree as ET
import numpy as np
from transforms3d.euler import euler2mat, mat2euler
from abc import ABC
from utils import parse_numstr, create_numstr


class PartConverter(ABC):
    def __init__(self, part_type):
        self.partType = part_type
        self.attribs = ['id', 'partType', 'position',
                        'rotation', 'commandPodId', 'materials']
        self.prerotation_matrix = None

    def prerotate(self, part: ET.Element):
        """Prerotate the part to match the orientation"""
        angles = parse_numstr(part.get('rotation'))
        angles = [n * np.pi/180 for n in angles]
        M = euler2mat(*[angles[n] for n in (2, 0, 1)], 'szxy')
        angles = mat2euler(np.matmul(M, self.prerotation_matrix), 'szxy')
        angles = [angles[n] * 180/np.pi for n in (1, 2, 0)]
        part.set('rotation', create_numstr(angles))

    @staticmethod
    def add_drag(part: ET.Element):
        """Adds drag to the part"""
        raw_drag = part.get('drag')
        drag = parse_numstr(raw_drag)
        area = [1.5*x for x in drag]
        raw_area = create_numstr(area)
        ET.SubElement(part, 'Drag', {'drag': raw_drag, 'area': raw_area})

    def convert_common(self, part: ET.Element, scale):
        """Converts parameters relevant to all parts"""
        part.set('commandPodId', '0')
        part.set('partType', self.partType)

        if scale != 1:
            position = parse_numstr(part.get('position'))
            position = [scale * x for x in position]
            raw_position = create_numstr(position)
            part.set('position', raw_position)

        if self.prerotation_matrix is not None:
            self.prerotate(part)

        materials = part.get('materials')
        part.set('materials', ','.join(materials.split(',')[0:1] * 5))

        ET.SubElement(part, 'Config')

        self.add_drag(part)

    def convert_specific(self, part: ET.Element, scale):
        """Converts parameters specific to the part"""
        pass

    def pop_attribs(self, part: ET.Element):
        """Pops unnecessary attribs of the part"""
        part.attrib = {x: part.attrib[x] for x in part.attrib if x in self.attribs}

    def convert(self, part: ET.Element, scale=1):
        """Converts the part from SP to SR2"""
        self.convert_common(part, scale)
        self.convert_specific(part, scale)
        self.pop_attribs(part)


class FuselageConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Fuselage1')
        self.prerotation_matrix = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        self.attribs.append('texture')

    def convert_specific(self, part: ET.Element, scale):
        part.set('texture', 'Default')

        tank = part.find('FuelTank.State')
        if tank is not None:
            tank.tag = 'FuelTank'
            tank.attrib.pop('fuel')

        fuselage = part.find('Fuselage.State')
        fuselage.tag = 'Fuselage'

        raw_bottom_scale = fuselage.get('rearScale')
        bottom_scale = parse_numstr(raw_bottom_scale)
        bottom_scale = [scale * x/4 for x in bottom_scale]
        fuselage.set('bottomScale', create_numstr(bottom_scale))

        raw_top_scale = fuselage.get('frontScale')
        top_scale = parse_numstr(raw_top_scale)
        top_scale = [scale * x/4 for x in top_scale]
        fuselage.set('topScale', create_numstr(top_scale))

        corner_tr = [0.0, 0.4, 1.0, 1.0]
        raw_corner_types = fuselage.get('cornerTypes')
        corner_types = parse_numstr(raw_corner_types)
        corner_types = [corner_tr[int(n)] for n in corner_types]
        corner_types[0], corner_types[2] = corner_types[2], corner_types[0]
        corner_types[4], corner_types[6] = corner_types[6], corner_types[4]
        fuselage.set('cornerRadiuses', create_numstr(corner_types))

        offset = parse_numstr(fuselage.get('offset'))
        offset = [scale * x/4 for x in offset]
        offset[1], offset[2] = offset[2], offset[1]
        offset[0] *= -1
        fuselage.set('offset', create_numstr(offset))

        for x in ['version', 'rearScale', 'frontScale',
                  'buoyancy', 'deadWeight', 'fuelPercentage',
                  'cornerTypes', 'scale', 'autoSizeOnConnected']:
            fuselage.attrib.pop(x, None)

class NoseConeConverter(FuselageConverter):
    def __init__(self):
        super().__init__()
        self.partType = 'NoseCone1'
        self.prerotation_matrix = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])

    def convert_specific(self, part: ET.Element, scale):
        super().convert_specific(part, scale)

        fuselage = part.find('Fuselage')

        top_scale = fuselage.get('topScale')
        fuselage.set('topScale', '0,0')
        fuselage.set('bottomScale', top_scale)

        corner_radiuses = parse_numstr(fuselage.get('cornerRadiuses'))
        corner_radiuses[0], corner_radiuses[1] = corner_radiuses[1], corner_radiuses[0]
        corner_radiuses[2], corner_radiuses[3] = corner_radiuses[3], corner_radiuses[2]
        corner_radiuses = corner_radiuses[4:]+corner_radiuses[:4]
        fuselage.set('cornerRadiuses', create_numstr(corner_radiuses))

        offset = parse_numstr(fuselage.get('offset'))
        offset[2] *= -1
        fuselage.set('offset', create_numstr(offset))

class InletConverter(FuselageConverter):
    def __init__(self):
        super().__init__()
        self.partType = 'Inlet1'

    def convert_specific(self, part: ET.Element, scale):
        super().convert_specific(part, scale)
        fuselage = part.find('Fuselage')
        for x in ['inletSlant', 'inletTrimSize',
                  'inletThicknessFront', 'inletThicknessRear']:
            fuselage.attrib.pop(x, None)

class WingConverter(PartConverter):
    def __init__(self, scale):
        super().__init__(part_type='Wing1')

    def convert_specific(self, part: ET.Element, scale):
        tank = part.find('FuelTank.State')
        part.remove(tank)

        wing = part.find('Wing.State')
        wing.tag = 'Wing'

        if scale != 1:
            for attrib_name in ('rootLeadingOffset', 'rootTrailingOffset',
                                'tipLeadingOffset', 'tipPosition', 'tipTrailingOffset'):
                raw_attrib = wing.get(attrib_name)
                attrib_val = parse_numstr(raw_attrib)
                attrib_val = [scale * x for x in attrib_val]
                wing.set(attrib_name, create_numstr(attrib_val))

        control_surfaces = wing.findall('ControlSurface')
        for surface in control_surfaces:
            inp = surface.get('inputId')
            surface.set('input', inp)
            surface.attrib.pop('inputId', None)
            if scale != 1:
                for attrib_name in ('start', 'end'):
                    raw_attrib = surface.get(attrib_name)
                    attrib_val = parse_numstr(raw_attrib)
                    attrib_val = [int(scale * x) for x in attrib_val]
                    surface.set(attrib_name, create_numstr(attrib_val))
            wing.remove(surface)
        part.extend(control_surfaces)
