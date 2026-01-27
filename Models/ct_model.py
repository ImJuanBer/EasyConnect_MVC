import math

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

    def run(self, data: dict) -> dict:
        inp = self._parse_inputs(data)

        out = {}  # aquí juntamos TODO lo que el UI necesita

        # 1) Amps Calculation
        out.update(self._calc_amps(inp))



        return out

    # ========= MODEL HELPERS =========
    def _parse_inputs(self, data: dict) -> dict:
        # conviertes tipos aquí (lo mínimo)
        return {
            "so": data.get("so", ""),
            "transformer_kVA": float(data.get("transformer_kVA") or 0),
            "HV_voltage": float(data.get("HV_voltage") or 0),
            "LV_voltage": float(data.get("LV_voltage") or 0),
            "cooling_class": data.get("cooling_class", ""),
            "CTH1_tag": data.get("CTH1_tag", ""),
            "Bushing_OD": float(data.get("Bushing_OD") or 0),
        }

    # ========= MODEL FUNCTIONS =========
    def _calc_amps(self, inp: dict) -> dict:
        kva = inp["transformer_kVA"]
        hv = inp["HV_voltage"]
        lv = inp["LV_voltage"]

        if hv <= 0 or lv <= 0:
            return {"HV_amps": "", "LV_amps": ""}

        hv_amps = kva * 1000 / (1.732 * hv * 1000)
        lv_amps = kva * 1000 / (1.732 * lv)

        return {
            "HV_amps": f"{hv_amps:.2f}",
            "LV_amps": f"{lv_amps:.2f}",
        }