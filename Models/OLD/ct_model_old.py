from pyautocad import Autocad
import pythoncom
import win32com.client
import time
import re


class CTModel:

    @staticmethod
    def APoint(x, y, z=0):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))

    def __init__(self):

        self.all_leads_qty = None
        self.pyacad = Autocad()
        self.lista_ct_tb_tag = list()
        self.lista_ct_tag = list()
        self.dict_tags = {"CT_TAG": self.lista_ct_tag, "TB_CT_TAG": self.lista_ct_tag}

        self.wire_count = 0
        self.idx_box = 0
    def create_ct_hv(self, acadModel, xpos, ypos):

        espaciado_extra_entre_grupos = 1
        x_pos = xpos
        y_pos = ypos

        # Diccionario de configuración de cada grupo  { Nombre Grupo : Configuracion }
        cts_config = {
            "CT1": {"CT_RATIO": "600:5 MR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "Predefined", "CT_TYPE": "protection"},

            "CT2": {"CT_RATIO": "2000:5 MR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "WTI", "CT_TYPE": "protection"},

            "CT3": {"CT_RATIO": "100:5 SR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "Predefined", "CT_TYPE": "protection"},
        }
        # Parámetros de espaciado

        espaciado_vertical_entre_cts = 6  # Espacio entre grupos (Y)

        #  LOCAL DEFINITIONS

        self.delta_x = 0

        def insert_CT_block(real_tag_param, tb_real_tag_param, leads):
            """Function only used in CTs construction"""

            block = acadModel.InsertBlock(self.APoint(x_pos, y_pos), f"CT_{leads}", 1, 1, 1, 0)

            for ct_attribute in block.GetAttributes():

                if ct_attribute.TagString.strip().upper() == "CT_RATIO":
                    ct_attribute.TextString = f"{ct_ratio}"  # This is the value in CAD blocks

                elif ct_attribute.TagString.strip().upper() == "CT_ACCY":
                    ct_attribute.TextString = f"{ct_accy}"  # This is the value in CAD blocks

                elif ct_attribute.TagString.strip().upper() == "CT_TB_PN":
                    ct_attribute.TextString = f"{tb_real_tag_param}"  # This is the value in CAD blocks

                elif ct_attribute.TagString.strip().upper() == "CT_PN":
                    ct_attribute.TextString = f"{real_tag_param}"  # This is the value in CAD blocks

                elif ct_attribute.TagString.strip().upper() == "ID":
                    ct_attribute.TextString = f"{real_tag_param}"  # This is the value in CAD blocks


                elif ct_attribute.TagString.strip().upper().startswith("JB_WIRE"):
                    if self.wire_count == 1:
                        self.junction_box_block = acadModel.InsertBlock(self.APoint(110 + self.delta_x, 50),
                                                                   f"JB_{cajas[self.idx_box]}", 1, 1, 1, 0)
                        for jb_attribute in self.junction_box_block.GetAttributes():
                            if jb_attribute.TagString.strip().upper() == "JB_ID":
                                jb_attribute.TextString = f"JBX{self.idx_box + 1}"  # This is the value in CAD blocks
                    if self.wire_count >= cajas[self.idx_box]:

                        self.idx_box += 1
                        self.delta_x += 10 #Distancia HORIZONTAL entre Junction boxes

                        self.junction_box_block = acadModel.InsertBlock(self.APoint(110 + self.delta_x, 50),
                                                                   f"JB_{cajas[self.idx_box]}", 1, 1, 1, 0)
                        for jb_attribute in self.junction_box_block.GetAttributes():
                            if jb_attribute.TagString.strip().upper() == "JB_ID":
                                jb_attribute.TextString = f"JBX{self.idx_box + 1}"  # This is the value in CAD blocks

                        if self.idx_box >= len(cajas):
                            raise RuntimeError("No hay cajas suficientes para alojar todos los leads.")
                        self.wire_count = 1  # reset enumeración en nueva caja
                    else:
                        self.wire_count += 1

                    ct_attribute.TextString = f"JBX{self.idx_box+1}-{self.wire_count}"  # Numeracion de CTs por fase
                    # Refresh
                time.sleep(0.01)
                ct_attribute.Update()



        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # LOGIC ONLY FOR CTS & JB CONSTRUCTION
        pins_qty = 0
        pins_list = list()
        for enum, (ct_tag_id, ct_params_list) in enumerate(cts_config.items()):

            H0_CTS = ct_params_list["H0"]  # Of CT's per Phase H0
            H1_CTS = ct_params_list["H1"]  # Of CT's per Phase H1
            H2_CTS = ct_params_list["H2"]  # Of CT's per Phase H2
            H3_CTS = ct_params_list["H3"]  # Of CT's per Phase H3
            leads_qty = ct_params_list["leads"]  # of leads

            # START OF JUNCTION BOX LOGIC
            max_pins_e_ct_group = (H0_CTS + H1_CTS + H2_CTS + H3_CTS) * leads_qty
            pins_qty += max_pins_e_ct_group
            pins_list.append(pins_qty)


        sizes = tuple(sorted((36, 16), reverse=True))  # (36,16,7)
        max_size = sizes[0]

        cajas = [max_size] * (pins_qty // max_size)
        residual = pins_qty % max_size

        if residual > 0:
            # escoger la caja más pequeña que cubra el residuo
            for s in sorted(sizes):
                if s >= residual:
                    cajas.append(s)
                    break
            else:
                # por seguridad (no debería ocurrir con sizes que incluyen max_size)
                cajas.append(max_size)

        print(pins_qty)
        print(cajas)


        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # START OF CTS CONSTRUCTION
        for enum, (ct_tag_id, ct_params_list) in enumerate(cts_config.items()):

            group_base_y = y_pos
            ct_ratio = ct_params_list["CT_RATIO"]
            ct_accy = ct_params_list["CT_ACCY"]
            H0_CTS = ct_params_list["H0"]
            H1_CTS = ct_params_list["H1"]
            H2_CTS = ct_params_list["H2"]
            H3_CTS = ct_params_list["H3"]
            leads_qty = ct_params_list["leads"]
            ct_application = ct_params_list["CT_APPLICATION"]

            for ct_per_phase in range(H0_CTS):
                # Make TAG for current transformer
                real_tag = f"{ct_tag_id}-H0{ct_per_phase + 1}"
                self.lista_ct_tag.append(real_tag)

                if ct_application == "WTI":
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBWTI{m.group(1)}-H0{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)
                else:
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBX{m.group(1)}-H0{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)

                x_pos = xpos
                y_pos = group_base_y - ct_per_phase * espaciado_vertical_entre_cts


                insert_CT_block(real_tag, tb_real_tag, leads_qty)

            for ct_per_phase in range(H1_CTS):
                # Make TAG for current transformer
                real_tag = f"{ct_tag_id}-H1{ct_per_phase + 1}"
                self.lista_ct_tag.append(real_tag)
                if ct_application == "WTI":
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBWTI{m.group(1)}-H1{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)
                else:
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBX{m.group(1)}-H1{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)

                x_pos = xpos + 10
                y_pos = group_base_y - (ct_per_phase * espaciado_vertical_entre_cts)

                insert_CT_block(real_tag, tb_real_tag, leads_qty)

            for ct_per_phase in range(H2_CTS):
                # Make TAG for current transformer
                real_tag = f"{ct_tag_id}-H2{ct_per_phase + 1}"
                self.lista_ct_tag.append(real_tag)
                if ct_application == "WTI":
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBWTI{m.group(1)}-H2{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)
                else:
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBX{m.group(1)}-H2{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)

                x_pos = xpos + 20
                y_pos = group_base_y - (ct_per_phase * espaciado_vertical_entre_cts)

                insert_CT_block(real_tag, tb_real_tag, leads_qty)

            for ct_per_phase in range(H3_CTS):
                # Make TAG for current transformer
                real_tag = f"{ct_tag_id}-H3{ct_per_phase + 1}"
                self.lista_ct_tag.append(real_tag)
                if ct_application == "WTI":
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBWTI{m.group(1)}-H3{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)
                else:
                    # Make TAG for terminal block
                    m = re.search(r"(\d+)$", ct_tag_id)
                    tb_real_tag = f"TBX{m.group(1)}-H3{ct_per_phase + 1}" if m else ct_tag_id
                    self.lista_ct_tb_tag.append(tb_real_tag)

                x_pos = xpos + 30
                y_pos = group_base_y - (ct_per_phase * espaciado_vertical_entre_cts)

                insert_CT_block(real_tag, tb_real_tag, leads_qty)

            max_rows = max(H0_CTS, H1_CTS, H2_CTS, H3_CTS)
            group_height = max_rows * espaciado_vertical_entre_cts
            y_pos = group_base_y - group_height - espaciado_extra_entre_grupos

            # END OF LOGIC FOR CTS CONSTRUCTION
            # --------------------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------------------

        # USEFUL OUTPUTS FOR CTS
        print(self.dict_tags)  # Dict containing device tags
        print(len(self.dict_tags["CT_TAG"]))
