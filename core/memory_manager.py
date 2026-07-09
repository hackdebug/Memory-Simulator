class MemoryBlock:
    def __init__(self, block_id, start_address, size):
        self.block_id = block_id
        self.start_address = start_address
        self.size = size
        self.is_free = True
        self.process_id = None

        def __repr__(self):
            status = "Libre" if self.is_free else f"Ocupado por proceso {self.process_id}"
            return f"[Bloque {self.block_id} | Comienza: {self.start_address} | Tamaño: {self.size} | Estado: {status}]"

class MemoryManager:
    def __init__(self, total_size):
        self.total_size = total_size
        self.block_list = [MemoryBlock(block_id=1, start_address=0, size=total_size)]
        self.block_counter = 1
    
    def get_free_block(self):
        return [b for b in self.block_list if b.is_free]
    
    def allocate_process(self, process_id, process_size, strategy="First Fit"):
        free_block = self.get_free_block()
        chosen_block = None

        if strategy == "First Fit":
            for b in free_block:
                if b.size >= process_size:
                    chosen_block = b
                    break

        elif strategy == "Best Fit":
            candidates = [b for b in free_block if b.size >= process_size]
            if candidates:
                chosen_block = candidates[0]
                for b in candidates:
                    if b.size < chosen_block.size:
                        chosen_block = b
        
        elif strategy == "Worst Fit":
            candidates = [b for b in free_block if b.size >= process_size]
            if candidates:
                chosen_block = candidates[0]
                for b in candidates:
                    if b.size > chosen_block.size:
                        chosen_block = b

        if chosen_block:
            if chosen_block.size > process_size:
                self.block_counter += 1
                new_free_block = MemoryBlock(
                    block_id=self.block_counter,
                    start_address=chosen_block.start_address + process_size,
                    size=chosen_block.size - process_size
                )

                idx = self.block_list.index(chosen_block)
                self.block_list.insert(idx + 1, new_free_block)

            chosen_block.size = process_size
            chosen_block.is_free = False
            chosen_block.process_id = process_id
            return True
        
        return False
    
    def deallocate_process(self, process_id):
        for b in self.block_list:
            if not b.is_free and b.process_id == process_id:
                b.is_free = True
                b.process_id = None
                self._merge_adjacent_free_block()
                return True
        return False
    
    def _merge_adjacent_free_block(self):
        i = 0
        while i < len(self.block_list) - 1:
            current_b = self.block_list[i]
            next_b = self.block_list[i + 1]
            if current_b.is_free and next_b.is_free:
                current_b.size += next_b.size
                self.block_list.pop(i + 1)
            else:
                i += 1

    def calculate_external_fragmentation(self, requested_size):
        total_free_space = sum(b.size for b in self.get_free_block())

        for b in self.get_free_block():
            if b.size >= requested_size:
                return 0
            
        return total_free_space