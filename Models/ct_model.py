from pyautocad import Autocad
import pythoncom
import win32com.client

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
    def create_ct_hv(self):

        # Diccionario de configuración de cada grupo  { Nombre Grupo : Configuracion }
        cts_config = {
            "CT1": {"CT_RATIO": "600:5 MR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "Predefined", "CT_TYPE": "protection"},

            "CT2": {"CT_RATIO": "2000:5 MR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "WTI", "CT_TYPE": "protection"},

            "CT3": {"CT_RATIO": "100:5 SR", "CT_ACCY": "C400", "H0": 1, "H1": 1, "H2": 1, "H3": 1, "leads": 5,
                    "CT_APPLICATION": "Predefined", "CT_TYPE": "protection"},
        }
