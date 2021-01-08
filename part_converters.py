import xml.etree.ElementTree as ET
import numpy as np
from transforms3d.euler import euler2mat, mat2euler
from abc import ABC
from utils import parse_numstr, create_numstr


class PartConverter(ABC):
    def __init__(self, part_type):
        self.part_type = part_type
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
        part.set('partType', self.part_type)

        part_scale = parse_numstr(part.get('scale', '1,1,1'))
        if scale != 1:
            position = parse_numstr(part.get('position'))
            position = [scale * x for x in position]
            raw_position = create_numstr(position)
            part.set('position', raw_position)
            part_scale = [scale * x for x in part_scale]

        if self.prerotation_matrix is not None:
            self.prerotate(part)

        materials = part.get('materials')
        part.set('materials', ','.join(materials.split(',')[0:1] * 5))

        config = ET.SubElement(part, 'Config')
        if part_scale != [1, 1, 1]:
            config.set('partScale', create_numstr(part_scale))

        self.add_drag(part)

    def convert_specific(self, part: ET.Element):
        """Converts parameters specific to the part"""
        pass

    def pop_attribs(self, part: ET.Element):
        """Pops unnecessary attribs of the part"""
        part.attrib = {x: part.attrib[x] for x in part.attrib if x in self.attribs}

    def convert(self, part: ET.Element, scale=1):
        """Converts the part from SP to SR2"""
        self.convert_common(part, scale)
        self.convert_specific(part)
        self.pop_attribs(part)

class BlockConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Block1')

    def convert_specific(self, part: ET.Element):
        adaptive_block = part.find('AdaptiveBlock.State')
        if adaptive_block is not None:
            part.remove(adaptive_block)

class FuselageConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Fuselage1')
        self.prerotation_matrix = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        self.attribs.append('texture')

    def convert_specific(self, part: ET.Element):
        part.set('texture', 'Default')

        config = part.find('Config')
        raw_part_scale = config.get('partScale')
        if raw_part_scale:
            part_scale = parse_numstr(raw_part_scale)
            part_scale[1], part_scale[2] = part_scale[2], part_scale[1]
            config.set('partScale', create_numstr(part_scale))

        tank = part.find('FuelTank.State')
        if tank is not None:
            tank.tag = 'FuelTank'
            tank.attrib.pop('fuel')

        fuselage = part.find('Fuselage.State')
        fuselage.tag = 'Fuselage'

        raw_bottom_scale = fuselage.get('rearScale')
        bottom_scale = parse_numstr(raw_bottom_scale)
        bottom_scale = [x/4 for x in bottom_scale]
        fuselage.set('bottomScale', create_numstr(bottom_scale))

        raw_top_scale = fuselage.get('frontScale')
        top_scale = parse_numstr(raw_top_scale)
        top_scale = [x/4 for x in top_scale]
        fuselage.set('topScale', create_numstr(top_scale))

        corner_tr = [0.0, 0.4, 1.0, 1.0]
        raw_corner_types = fuselage.get('cornerTypes')
        corner_types = parse_numstr(raw_corner_types)
        corner_types = [corner_tr[int(n)] for n in corner_types]
        corner_types[0], corner_types[2] = corner_types[2], corner_types[0]
        corner_types[4], corner_types[6] = corner_types[6], corner_types[4]
        fuselage.set('cornerRadiuses', create_numstr(corner_types))

        offset = parse_numstr(fuselage.get('offset'))
        offset = [x/4 for x in offset]
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
        self.part_type = 'NoseCone1'
        self.prerotation_matrix = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])

    def convert_specific(self, part: ET.Element):
        super().convert_specific(part)

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
        self.part_type = 'Inlet1'

    def convert_specific(self, part: ET.Element):
        super().convert_specific(part)
        fuselage = part.find('Fuselage')
        for x in ['inletSlant', 'inletTrimSize',
                  'inletThicknessFront', 'inletThicknessRear']:
            fuselage.attrib.pop(x, None)

class WingConverter(PartConverter):
    def __init__(self):
        super().__init__(part_type='Wing1')

    def convert_specific(self, part: ET.Element):
        tank = part.find('FuelTank.State')
        part.remove(tank)

        wing = part.find('Wing.State')
        wing.tag = 'Wing'

        control_surfaces = wing.findall('ControlSurface')
        for surface in control_surfaces:
            inp = surface.get('inputId')
            surface.set('input', inp)
            surface.attrib.pop('inputId', None)
            wing.remove(surface)
        part.extend(control_surfaces)

class AbstractRotatorConverter(PartConverter):
    def __init__(self, part_type):
        super().__init__(part_type=part_type)
        self.attribs.append('activationGroup')
        self.inputs = {'VTOL': 'Slider1', 'Trim': 'Slider2'}

    def convert_input_controller(self, part: ET.Element, input_id: str):
        input_controller = part.find('InputController.State')
        input_controller.tag = 'InputController'
        raw_input = input_controller.get('input')
        raw_input = self.inputs.get(raw_input, raw_input)
        input_controller.set('input', raw_input)
        input_controller.set('inputId', input_id)

        activation_group = input_controller.get('activationGroup')
        if activation_group:
            part.set('activationGroup', activation_group)
            input_controller.attrib.pop('activationGroup')

    def convert_specific(self, part: ET.Element):
        raise NotImplementedError

class PistonConverter(AbstractRotatorConverter):
    def __init__(self):
        super().__init__(part_type='Piston1')

    def convert_specific(self, part: ET.Element):
        self.convert_input_controller(part, 'Piston')
        piston = part.find('Piston.State')
        piston.tag = 'Piston'

class SmallRotatorConverter(AbstractRotatorConverter):
    def __init__(self):
        super().__init__(part_type='Rotator1')
        self.prerotation_matrix = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

    def convert_specific(self, part: ET.Element):
        self.convert_input_controller(part, 'Rotator')
        joint_rotator = part.find('JointRotator.State')
        joint_rotator.tag = 'JointRotator'

        config = part.find('Config')
        raw_part_scale = config.get('partScale')
        if raw_part_scale:
            part_scale = parse_numstr(raw_part_scale)
            part_scale[1], part_scale[2] = part_scale[2], part_scale[1]
            config.set('partScale', create_numstr(part_scale))

class HingeRotatorConverter(AbstractRotatorConverter):
    def __init__(self):
        super().__init__(part_type='HingeRotator1')
        self.prerotation_matrix = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])

    def convert_specific(self, part: ET.Element):
        self.convert_input_controller(part, 'Rotator')
        joint_rotator = part.find('JointRotator.State')
        joint_rotator.tag = 'JointRotator'

        config = part.find('Config')
        raw_part_scale = config.get('partScale')
        if raw_part_scale:
            part_scale = parse_numstr(raw_part_scale)
            part_scale[0], part_scale[1], part_scale[2] = part_scale[1], part_scale[2], part_scale[0]
            config.set('partScale', create_numstr(part_scale))


CONVERTERS = {'Fuselage-Body-1': FuselageConverter(),
              'Wing-3': WingConverter(),
              'Fuselage-Cone-1': NoseConeConverter(),
              'Fuselage-Inlet-1': InletConverter(),
              'Block-1': BlockConverter(),
              'Piston': PistonConverter(),
              'SmallRotator-1': SmallRotatorConverter(),
              'HingeRotator-1': HingeRotatorConverter()}
CONVERTERS['Wing-2'] = CONVERTERS['Wing-3']
CONVERTERS['Fuselage-Hollow-1'] = CONVERTERS['Fuselage-Body-1'] # an inlet would be better but attachment points won't translate well
CONVERTERS['Block-2'] = CONVERTERS['Block-1']
