from openpyxl import Workbook
from io import BytesIO


class logger:
    def __init__(self):
        self.logs = {}

    def add(self, order_id: int):
        self.logs[order_id] = {
            "subs":[]
        }


    def add_sub(self, order_id: int, item_id: int, print_type: str, status: str, info: str = ""):
        if order_id not in self.logs:
            self.add(order_id, status="")
            
        self.logs[order_id]["subs"].append({
            "id": item_id,
            "print_type": print_type,
            "status": status,
            "info": info
        })



    def get(self) -> list[str]:
        accepted_logs = ""
        cancelled_logs = ""
        
        wb = Workbook()
        excel = wb.active
        excel.title = "Accepted Subs"
        excel.append(["ID", "Тип друку"])
        
        cache = []

        for id, order in self.logs.items():
            # Статуси всіх підзамовлень
            statuses = set(sub["status"].split(".")[0] for sub in order["subs"])
            
            # Якщо є хоч один скасований піделемент
            if "Скасовано" in statuses:
                cancelled_logs += f"\n\n\n\nЗамовлення номер - {id}:"
            if "Створено успішно" in statuses:
                accepted_logs += f"\n\n\n\nЗамовлення номер - {id}:"

            for sub in order["subs"]:
                if "Скасовано" in sub["status"]:
                    cancelled_logs += f"\n\n{sub['info']}\nСтатус: {sub['status']}"
                elif "Створено успішно" in sub["status"]:
                    accepted_logs += f"\n\n{sub['info']}\nСтатус: {sub['status']}"
                    
                    excel.append([sub.get("id", "N/A"), sub.get("print_type", "N/A")])
                    cache.append(sub.get("id", "N/A"))


        excel_io = BytesIO()
        wb.save(excel_io)
        excel_io.seek(0)

        return accepted_logs, cancelled_logs, excel_io, cache