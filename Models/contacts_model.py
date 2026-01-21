from pyautocad import Autocad
import pythoncom
import win32com.client
import time
import re

class ContactsModel:

    @staticmethod
    def APoint(x, y, z=0):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))

    def __init__(self):

        self.pyacad = Autocad()

    def create_contacts(self, acadModel, xpos, ypos, cooling_stage, rise, contactos_config):

        # Diccionario de configuración de cada grupo  { Nombre Grupo : Configuracion }

        # Parámetros de espaciado
        espaciado_horizontal_entre_contactos = 12  # Espacio entre contactos dentro del grupo (X)
        espaciado_vertical_entre_grupos = 12  # Espacio entre grupos (Y)

        self.x_ref_from_device_list = list()

        # Recorremos cada grupo
        for group, (nombre_grupo, config) in enumerate(contactos_config.items()):
            self.contacts_count = 0
            device_name = config["device_name"]
            tag_id = config["tag_id"]
            number_contacts = config["number_contacts"]

            # Y base para este grupo (una fila por grupo)
            y_base = ypos + (-group * espaciado_vertical_entre_grupos)

            for i in range(number_contacts):
                x_pos = xpos + (i * espaciado_horizontal_entre_contactos)  # contacto horizontal
                # Insert Blocks
                block = acadModel.InsertBlock(self.APoint(x_pos, y_base), "Contact", 1, 1, 1, 0)
                block.XScaleFactor = 1
                block.YScaleFactor = 1
                block.ZScaleFactor = 1
                time.sleep(0.01)
                # Actualizar atributos

                # --- Reemplazo directo del bloque de atributos con contador TBX secuencial ---

                # todo: For oil temperature geuges

                # For one fan stage
                if number_contacts == 3 and tag_id.startswith("26Q") and cooling_stage == "ONAF" and rise == "55":
                    descriptions = ["FAN @ 60°C", "ALARM @ 80°C ", "TRIP @ 90°C "]
                elif number_contacts == 3 and tag_id.startswith("26Q") and cooling_stage == "ONAF" and rise == "55/65":
                    descriptions = ["FAN @ 60°C", "ALARM @ 90°C ", "TRIP @ 105°C "]
                elif number_contacts == 3 and tag_id.startswith("26Q") and cooling_stage == "ONAF" and rise == "65":
                    descriptions = ["FAN @ 75°C", "ALARM @ 90°C ", "TRIP @ 105°C "]

                # For two FAN stages
                elif number_contacts == 4 and tag_id.startswith(
                        "26Q") and cooling_stage == "ONAF/ONAF" and rise == "55":
                    descriptions = ["FAN 1 @ 55°C", "FAN 2 @ 60°C", "ALARM @ 80°C ", "TRIP @ 90°C "]
                elif number_contacts == 4 and tag_id.startswith(
                        "26Q") and cooling_stage == "ONAF/ONAF" and rise == "55/65":
                    descriptions = ["FAN 1 @ 55°C", "FAN 2 @ 60°C" "ALARM @ 90°C ", "TRIP @ 105°C "]
                elif number_contacts == 4 and tag_id.startswith(
                        "26Q") and cooling_stage == "ONAF/ONAF" and rise == "65":
                    descriptions = ["FAN 1 @ 65°C", "FAN 2 @ 75°C" "ALARM @ 90°C ", "TRIP @ 105°C "]

                else:
                    descriptions = [f"CONTACT {j + 1}" for j in range(number_contacts)]

                # todo: For Winding temperature indicators

                # todo: For Oil level gauges

                # todo: For Pressure Relief Gauges

                #######################################################################
                #######################################################################
                #Wiresets para DESCRIPTION
                WIRE_SETS = [
                    ["BLK", "RED", "BLU"],  # 1er contacto
                    ["ORG", "YEL", "BRN"],  # 2º contacto
                    ["RED/BLK", "BLU/BLK", "ORG/BLK"],  # 3er contacto
                    ["YEL/BLK", "BRN/BLK", "BLK/RED"],  # 4º contacto
                ]
                # contacto actual: usa i (0-based) -> contact_idx (1-based)
                contact_idx = i + 1
                colors = WIRE_SETS[(contact_idx - 1) % len(WIRE_SETS)]
                _wire_idx_regex = re.compile(r"^WIRE[._\s-]*([0-9]+)$", re.IGNORECASE)
                #######################################################################
                #######################################################################

                # Primero, procesa NAME/DESCRIPTION/CONTACT_NO_1
                for contact_attribute in block.GetAttributes():
                    attribute = contact_attribute.TagString.strip().upper()

                    if attribute == "NAME":
                        contact_attribute.TextString = device_name

                    elif attribute == "DESCRIPTION":
                        contact_attribute.TextString = descriptions[i] if i < len(descriptions) else ""
                    elif attribute.startswith("WIRE"):
                        m = _wire_idx_regex.match(attribute)
                        if m:
                            try:
                                idx = int(m.group(1))  # 1, 2 o 3
                            except ValueError:
                                idx = None
                            if idx in (1, 2, 3):
                                contact_attribute.TextString = colors[idx - 1]
                            # si no matchea índice, lo ignoramos
                    elif attribute == "ID":
                        contact_attribute.TextString = tag_id
                    elif attribute == "GROUP":
                        contact_attribute.TextString = nombre_grupo

                    contact_attribute.Update()

                tbx_tags = {"TBX.1", "TBX.2", "TBX.3"}
                tbx_attrs = [att for att in block.GetAttributes()
                             if att.TagString.strip().upper() in tbx_tags]

                # Orden fijo por TagString para asegurar secuencia .1 -> .2 -> .3
                tbx_attrs.sort(key=lambda a: a.TagString.strip().upper())

                for att in tbx_attrs:
                    self.contacts_count += 1
                    xref_val = f"TB.{tag_id}{self.contacts_count}"
                    att.TextString = xref_val
                    att.Update()
                    # Registro:
                    self.x_ref_from_device_list.append(xref_val)

                # (opcional) refresca el bloque
                try:
                    block.Update()
                except:
                    pass


