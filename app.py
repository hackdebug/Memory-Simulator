from flask import Flask, render_template, request, jsonify
from core.memory_manager import MemoryManager
from core.mmu import MMU

app = Flask(__name__)

memory_manager = MemoryManager(total_size=1000)

mmu_manager = MMU(physical_memory_size=256, page_size=64)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/allocation/status', methods=['GET'])
def allocation_status():
    blocks = []
    for b in memory_manager.block_list:
        blocks.append({
            "block_id": b.block_id,
            "start_address": b.start_address,
            "size": b.size,
            "is_free": b.is_free,
            "process_id": b.process_id
        })
    return jsonify({"blocks": blocks})

@app.route('/allocation/allocate', methods=['POST'])
def allocation_allocate():
    data = request.json
    process_id = data.get('process_id')
    size = int(data.get('size'))
    strategy = data.get('strategy', 'First Fit')

    success = memory_manager.allocate_process(process_id, size, strategy)

    if success:
        return jsonify({"status": "success", "message": f"Proceso {process_id} asignado con éxito usando {strategy}."})
    else:
        frag_ext = memory_manager.calculate_external_fragmentation(size)
        return jsonify({
            "status": "error",
            "message": f"Error: No hay suficiente espacio contiguo para el proceso {process_id}.",
            "external_fragmentation": frag_ext
        })

@app.route('/allocation/deallocate', methods=['POST'])
def allocation_deallocate():
    data = request.json
    process_id = data.get('process_id')

    success = memory_manager.deallocate_process(process_id)

    if success:
        return jsonify({"status": "success", "message": f"Proceso {process_id} liberado y memoria compactada."})
    else:
        return jsonify({"status": "error", "message": f"Error: No se encontró el proceso {process_id}."})
    
@app.route('/mmu/create_process', methods=['POST'])
def mmu_create_process():
    data = request.json
    process_id = data.get('process_id')
    virtual_size = int(data.get('virtual_size'))

    success, message = mmu_manager.create_page_table(process_id, virtual_size)

    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message})
    
@app.route('/mmu/translate', methods=['POST'])
def mmu_translate():
    data = request.json
    process_id = data.get('process_id')
    virtual_address = int(data.get('virtual_address'))

    result = mmu_manager.translate_address(process_id, virtual_address)
    return jsonify(result)

@app.route('/mmu/fragmentation', methods=['GET'])
def mmu_fragmentation():
    total = mmu_manager.calculate_total_internal_fragmentation()
    return jsonify({"total_internal_fragmentation": total})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)