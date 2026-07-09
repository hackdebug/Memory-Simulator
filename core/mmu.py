class PageTableEntry:
    def __init__(self, page_number):
        self.page_number = page_number
        self.frame_number = None
        self.is_valid = False

class MMU:
    def __init__(self, physical_memory_size, page_size):
        self.physical_memory_size = physical_memory_size
        self.page_size = page_size

        self.total_frames = physical_memory_size

        self.available_frames = [True] * self.total_frames

        self.page_tables = {}
    
    def create_page_table(self, process_id, virtual_memory_size):
        num_pages = virtual_memory_size
        if virtual_memory_size % self.page_size != 0:
            num_pages += 1

        free_frames_count = self.available_frames_count(True)

        if num_pages > free_frames_count:
            return False, f"Error: No hay suficientes marcos físicos disponibles. Se requieren {num_pages} marcos."
        
        page_table = []
        for i in range(num_pages):
            entry = PageTableEntry(page_number=i)

            for frame_idx in range(self.total_frames):
                if self.available_frames[frame_idx]:
                    self.available_frames[frame_idx] = False # ocupar el marco
                    entry.frame_number = frame_idx
                    entry.is_valid = True
                    break
            
            page_table.append(entry)

        self.page_tables[process_id] = page_table
        return True, f"Tabla de páginas creada con éxito. Proceso asignado a {num_pages} marcos."
    
    def translate_address(self, process_id, virtual_address):
        if process_id not in self.page_tables:
            return {"status": "error", "message": f"Error: El proceso {process_id} no existe."}
        
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size

        page_table = self.page_tables[process_id]

        if page_number >= len(page_table):
            return {"status": "error", "message": "Error: Dirección virtual fuera de rango."}
        
        page_entry = page_table[page_number]

        if not page_entry.is_valid:
            return {"status": "error", "message": "Error: La página solicitada no está cargada en memoria física."}
        
        physical_address = (page_entry.frame_number * self.page_size) + offset

        return {
            "status": "success",
            "page_number": page_number,
            "offset": offset,
            "frame_number": page_entry.frame_number,
            "physical_address": physical_address,
            "message": f"Traducción exitosa: Dirección Virtual {virtual_address} -> Dirección Física {physical_address}"
        }
    
    def remove_process_pages(self, process_id):
        if process_id in self.page_tables:
            for entry in self.page_tables[process_id]:
                if entry.is_valid:
                    self.available_frames[entry.frame_number] = True
            
            del self.page_tables[process_id]
            return True
        return False