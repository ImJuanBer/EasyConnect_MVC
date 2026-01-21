from pyautocad import Autocad
import pythoncom
import win32com.client



class TBModel:

    @staticmethod
    def APoint(x, y, z=0):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))

    def __init__(self):

        self.pyacad = Autocad()
        self.blocks_list = list()

    def listar_tbx_por_id(self, acadModel):
        """
        Devuelve: { ID : [ID.1, ID.2, ..., ID.m] }
        - Agrupa TODOS los bloques que comparten el mismo ID.
        - m = suma total de atributos TBX.* hallados para ese ID (en todos sus bloques).
        - Dentro de cada bloque, respeta el orden por índice (TBX.1, TBX.2, ...).
        """
        self.tb_cross_ref_dict = {}  # {ID: [TB.WT1, TB.WT2, ...]}
        self.devices_cross_ref_dict = {}  #

        for blk in acadModel:
            if getattr(blk, "ObjectName", "") != "AcDbBlockReference":
                continue
            if not hasattr(blk, "GetAttributes"):
                continue

            id_val = None
            group_val = None
            try:
                for a in blk.GetAttributes():
                    if a.TagString.strip().upper() == "ID":
                        id_val = a.TextString.strip()
                        break
                for x in blk.GetAttributes():
                    if x.TagString.strip().upper() == "GROUP":
                        group_val = x.TextString.strip()
                        break

            except Exception:
                continue
            if not id_val:
                continue
            if not group_val:
                continue

            #  recolectar TBX.k del bloque actual
            tbx_indices = []
            #  recolectar WIRE.k del bloque actual
            wire_indices = []
            try:
                for attribute in blk.GetAttributes():
                    tag = attribute.TagString.strip().upper()
                    if tag.startswith("TBX."):
                        idx = tag[4:]
                        if idx.isdigit():
                            tbx_indices.append(int(idx))
                for attribute in blk.GetAttributes():
                    tag = attribute.TagString.strip().upper()
                    if tag.startswith("WIRE"):
                        wire = attribute.TextString
                        wire_indices.append(wire)

            except Exception:
                pass

            if not tbx_indices:
                # no hay patas TBX en este bloque; sigue con el siguiente
                continue
            if not wire_indices:
                # no hay patas wire en este bloque; sigue con el siguiente
                continue

            # inicializar acumulador por ID y secuencia
            if id_val not in self.tb_cross_ref_dict:
                self.tb_cross_ref_dict[id_val] = []
            if group_val not in self.devices_cross_ref_dict:
                self.devices_cross_ref_dict[group_val] = []

            lista_tb_cross_ref_dict = self.tb_cross_ref_dict[id_val]
            lista_devices_cross_ref_dict = self.devices_cross_ref_dict[group_val]
            next_num = len(lista_tb_cross_ref_dict) + 1  # siguiente índice global para este ID

            # Añade en orden TBX.1, TBX.2, ... del bloque actual
            for num in sorted(tbx_indices):
                lista_tb_cross_ref_dict.append(f"{id_val}.{next_num}")
                next_num += 1
            for sufix in wire_indices:  # [BLK, RED, BLU, BLK, RED, BLU]
                lista_devices_cross_ref_dict.append(f"{group_val}.{sufix}")

        # salida de control rápida (opcional)
        print(self.tb_cross_ref_dict)
        # print(self.devices_cross_ref_dict)
        print("\n")
        print("| ID                  | LISTA")
        print("|---------------------|------------------------------")
        for _id, vals in self.tb_cross_ref_dict.items():
            print(f"| {_id:<19} | {', '.join(vals)}")

        return self.tb_cross_ref_dict

    def _set_attr(self, bref, tag, text):
        """Escribe el atributo 'tag' si existe."""
        try:
            for a in bref.GetAttributes():
                if a.TagString.strip().upper() == tag.upper():
                    a.TextString = str(text)
                    break
        except Exception:
            pass

    def crear_terminal_blocks(self, acadModel, start_xy=(0.0, 0.0), dx=75.0, dy=-22.0,MAX_POR_COLUMNA = 20):
        x0, y0 = start_xy
        col = fila = 0

        tb_items = list(self.tb_cross_ref_dict.items())
        names_items = list(self.devices_cross_ref_dict.items())
        max_pairs = max(len(tb_items), len(names_items))

        for i in range(max_pairs):
            # toma par i-esimo de cada diccionario (si falta, usa vacío)
            dev_id, tb_list = tb_items[i] if i < len(tb_items) else (None, [])
            group_id, name_list = names_items[i] if i < len(names_items) else (None, [])

            # longitud por terminales a crear en este par
            n = max(len(tb_list), len(name_list))

            for k in range(1, n + 1):
                # valores por índice (si falta, fallback)
                conn = tb_list[k - 1] if k - 1 < len(tb_list) else ""  # no imprescindible si solo ubicas cantidad
                name = name_list[k - 1] if k - 1 < len(name_list) else f"MISSING{k}"

                x = x0 + col * dx
                y = y0 + fila * dy

                block = acadModel.InsertBlock(self.APoint(x, y, 0), "TB_1CONN", 1, 1, 1, 0)
                self.blocks_list.append(block)
                block.XScaleFactor = block.YScaleFactor = block.ZScaleFactor = 1

                #ID del primer diccionario para el atributo ID,
                self._set_attr(block, "ID", f"" if dev_id is None else f"{dev_id}{k}")
                self._set_attr(block, "L1", name)  # <- viene del devices_cross_ref_dict (group_id)
                self._set_attr(block, "L2", "")
                self._set_attr(block, "R1", "")
                self._set_attr(block, "R2", "")


                # grilla
                fila += 1
                if fila >= MAX_POR_COLUMNA:
                    fila = 0
                    col += 1
                if fila % 10 == 0:
                    block.Color = 1

        print(len(self.blocks_list))
