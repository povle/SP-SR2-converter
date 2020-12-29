import xml.etree.ElementTree as ET

command_pod = ET.Element('Part', {'id': '0', 'partType': 'CommandPod1', 'position': '0,0,0',
                                  'rotation': '90,0,0', 'rootPart': 'true', 'commandPodId': '0', 'materials': '0,0,0,0,0'})
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
                         'craftConfigType': 'Plane',
                         'pidPitch': '10,0,0',
                         'pidRoll': '0.6,0,0',
                         'pilotSeatRotation': '270,0,0'
                     })
ET.SubElement(cpod, 'Controls')
ET.SubElement(command_pod, 'Gyroscope')
ET.SubElement(command_pod, 'FuelTank')
ET.SubElement(command_pod, 'CrewCompartment')
