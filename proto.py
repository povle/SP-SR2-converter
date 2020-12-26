import xml.etree.ElementTree as ET
import uuid
import numpy as np
from transforms3d.euler import euler2mat, mat2euler

def parse_numstr(string: str):
    return [float(x) for x in string.split(',')]

def create_numstr(floats: list):
    return ','.join([str(round(x, 8)) for x in floats])


ROT = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
def rotate(angles: list):
    angles = [n * np.pi/180 for n in angles]
    M = euler2mat(*[angles[n] for n in (2, 0, 1)], 'szxy')
    angles = mat2euler(np.matmul(M, ROT), 'szxy')
    angles = [angles[n] * 180/np.pi for n in (1, 2, 0)]
    return angles


'''<Craft name='BL-S2GM4'
          boundsMin='-1.695318,1.721081,-1.695315'
          size='3.390636,11.66073,3.39063'
          theme='Default'
          url=''
          xmlVersion='6'>'''

'''<Craft name='sn1'
          parent=''
          initialBoundsMin='-0.8359594,-2.937141,-0.8359594'
          initialBoundsMax='0.8359594,3.326535,0.8359594'
          price='511859'
          suppressCraftConfigWarnings='false'
          xmlVersion='11'
          localCenterOfMass='0,-2.694861,0'>'''

'''<Craft name='Kepler Glider'
          parent=''
          initialBoundsMin='-21.4504,-2.260609,-12.14037'
          initialBoundsMax='21.49989,3.237475,14.4586'
          price='1889707'
          xmlVersion='5'>'''

tree = ET.parse('./test_crafts/TestCorners.xml')
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

'''<Part id='5'
         partType='Fuselage-Body-1'
         position='-9.237056E-14,12.81931,8.344654E-07'
         rotation='-4.829673E-06,270,180'
         drag='0,0,0,0,0,0'
         materials='0'>
        <FuelTank.State fuel='0' capacity='0' />
        <Fuselage.State version='2' frontScale='1,0.25' rearScale='1,0.25' offset='0,0,3' deadWeight='0' buoyancy='0' fuelPercentage='0' cornerTypes='0,0,0,0,0,0,0,0' />
      </Part>'''                                                                                                                                    #f1f2f3f4b1b2b3b4

'''<Part id='3'
         partType='Fuselage1'
         position='-0.0001023469,-0.05576409,11.47347'
         rotation='270.2273,1.817085E-05,-1.980841E-05'
         commandPodId='2'
         materials='0,0,2,3,4'>
        <Drag drag='0.07605563,0,0.8295473,0.9772433,0.6901614,0.7341061' area='0.4503731,0,1.069636,1.210377,0.9716101,1.036384' />
        <Config massScale='0' />
        <Fuselage bottomScale='0.725,0.675' fuelPercentage='0' cornerRadiuses="0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8" offset='0,0.4500164,5.960464E-08' topScale='0.8,0.8' />
        <FuelTank capacity='2184337' fuelType='Battery' />                    # f1  f2  f3  f4  b1  b2  b3  b4
      </Part>'''
# 0 = hard -> 0.0
# 1 = smooth -> 0.4
# 2 = curved -> 1.0*
# 3 = circular -> 1.0
# f1 -> f3
# f2 -> f2
# f3 -> f1
# f4 -> f4

part_ids = set()
for part in list(parts):
    if part.get('partType') != 'Fuselage-Body-1':
        parts.remove(part)
        continue

    part_ids.add(part.get('id'))
    part.set('partType', 'Fuselage1')

    part.set('commandPodId', '0')

    position = parse_numstr(part.get('position'))
    position = [2 * x for x in position]
    # position[1], position[2] = position[2], position[1]
    # position[2] *= -1
    raw_position = create_numstr(position)
    part.set('position', raw_position)

    rotation = parse_numstr(part.get('rotation'))
    rotation = rotate(rotation)
    part.set('rotation', create_numstr(rotation))

    materials = part.get('materials')
    part.set('materials', ','.join(materials.split(',')[0:1] * 5))

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

command_pod = ET.Element('Part', {'id': '0', 'partType': 'CommandPod1', 'position': '0,0,0',
                                  'rotation': '0,0,0', 'rootPart': 'true', 'commandPodId': '0', 'materials': '0,0,0,0,0'})
ET.SubElement(command_pod, 'Drag',
              {
                  'drag': '1.206616,1.204895,1.115982,0.02278123,1.084838,1.085515',
                  'area': '1.619598,1.619598,2.027669,0.03990095,1.489188,1.489188'
              })
ET.SubElement(command_pod, 'Config')
cpod = ET.SubElement(command_pod, 'CommandPod',
                     {
                         'activationGroupNames': ',,,,,,,Landing Gear,Solar Panels,RCS',
                         'activationGroupStates': 'false,' * 7 + 'true,false,true',
                         'pidPitch': '10,0,25',
                         'pidRoll': '10,0,25',
                         'pilotSeatRotation': '-90,0,0'
                     })
ET.SubElement(cpod, 'Controls')
ET.SubElement(command_pod, 'Gyroscope')
ET.SubElement(command_pod, 'FuelTank')
ET.SubElement(command_pod, 'CrewCompartment')
parts.insert(0, command_pod)

connections = assembly.find('Connections')
for conn in list(connections):
    a = conn.get('partA')
    b = conn.get('partB')
    if a not in part_ids or b not in part_ids:
        connections.remove(conn)

'''<Body angularVelocity='0,0,0'
         partIds='8,9,10'
         position='0,0,0'
         rotation='0,0,0'
         velocity='0,0,0' />'''

'''<Body id='2'
         partIds='13,20,152,153,154,155,156,157'
         mass='2.90837431'
         position='-0.0001022842,-0.02814794,4.538773'
         rotation='0,0,0'
         centerOfMass='0,0,0' />'''

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

designer_settings = ET.SubElement(craft, 'DesignerSettings', {'themeName': theme_name})
designer_settings.append(theme)

themes = ET.SubElement(craft, 'Themes')
themes.append(theme)

ET.SubElement(craft, 'Symmetry')

tree.write('test_results/test53.xml', encoding='utf-8', xml_declaration=True)
