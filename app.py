from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# Conexión a MongoDB
try:
    mongo_link = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_link, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    
    db = client['mi_tienda']
    productos_collection = db['productos']
    print("[OK] Conexion a MongoDB verificada y exitosa")
except Exception as e:
    print(f"[ERROR] Conexion MongoDB: {e}")
    productos_collection = None

@app.route('/')
def index():
    """Renderiza la página principal con la lista de productos"""
    try:
        if productos_collection is None:
            return render_template('index.html', productos=[])
        productos = list(productos_collection.find())
        return render_template('index.html', productos=productos)
    except Exception as e:
        print(f"[ERROR] obtener productos: {e}")
        return render_template('index.html', productos=[])

@app.route('/crear', methods=['POST'])
def crear():
    """Inserta un nuevo producto en MongoDB"""
    try:
        if productos_collection is None:
            print("[ERROR] Coleccion no disponible")
            return redirect(url_for('index'))
            
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '')
        stock = request.form.get('stock', '')

        print(f"[INFO] Recibido: nombre={nombre}, precio={precio}, stock={stock}")

        if not nombre:
            print("[WARN] Nombre vacio")
            return redirect(url_for('index'))
        
        precio = float(precio)
        stock = int(stock)
        print("[OK] Datos validados")

        nuevo_producto = {
            'nombre': nombre,
            'precio': precio,
            'stock': stock,
            'creado_en': datetime.now()
        }

        resultado = productos_collection.insert_one(nuevo_producto)
        print(f"[OK] Producto creado: {resultado.inserted_id}")

    except ValueError as ve:
        print(f"[ERROR] Validacion: {ve}")
    except Exception as e:
        print(f"[ERROR] Crear producto: {type(e).__name__}: {e}")

    return redirect(url_for('index'))

@app.route('/editar/<id>', methods=['POST'])
def editar(id):
    """Actualiza un producto existente"""
    try:
        if productos_collection is None:
            print("[ERROR] Coleccion no disponible")
            return redirect(url_for('index'))
            
        if not ObjectId.is_valid(id):
            print(f"[ERROR] ID invalido: {id}")
            return redirect(url_for('index'))

        object_id = ObjectId(id)
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '')
        stock = request.form.get('stock', '')

        print(f"[INFO] Editando: {object_id}")

        if not nombre:
            print("[WARN] Nombre vacio")
            return redirect(url_for('index'))

        precio = float(precio)
        stock = int(stock)

        producto_actualizado = {
            'nombre': nombre,
            'precio': precio,
            'stock': stock,
            'actualizado_en': datetime.now()
        }

        resultado = productos_collection.update_one(
            {'_id': object_id},
            {'$set': producto_actualizado}
        )

        if resultado.matched_count > 0:
            print(f"[OK] Producto actualizado: {object_id}")
        else:
            print(f"[WARN] Producto no encontrado: {object_id}")

    except ValueError as ve:
        print(f"[ERROR] Validacion: {ve}")
    except Exception as e:
        print(f"[ERROR] Editar producto: {type(e).__name__}: {e}")

    return redirect(url_for('index'))

@app.route('/eliminar/<id>', methods=['POST'])
def eliminar(id):
    """Elimina un producto por su ObjectId"""
    try:
        if productos_collection is None:
            print("[ERROR] Coleccion no disponible")
            return redirect(url_for('index'))
            
        if not ObjectId.is_valid(id):
            print(f"[ERROR] ID invalido: {id}")
            return redirect(url_for('index'))

        object_id = ObjectId(id)
        resultado = productos_collection.delete_one({'_id': object_id})

        if resultado.deleted_count > 0:
            print(f"[OK] Producto eliminado: {object_id}")
        else:
            print(f"[WARN] Producto no encontrado: {object_id}")

    except Exception as e:
        print(f"[ERROR] Eliminar producto: {type(e).__name__}: {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=puerto)
