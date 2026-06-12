from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# Conexión a MongoDB
try:
    client = MongoClient("MONGO_URI", "mongodb://localhost:27017")
    db = client['mi_tienda']
    productos_collection = db['productos']
    print("✓ Conexión a MongoDB exitosa")
except Exception as e:
    print(f"✗ Error al conectar a MongoDB: {e}")

@app.route('/')
def index():
    """Renderiza la página principal con la lista de productos"""
    try:
        productos = list(productos_collection.find())
        return render_template('index.html', productos=productos)
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return render_template('index.html', productos=[])

@app.route('/crear', methods=['POST'])
def crear():
    """Inserta un nuevo producto en MongoDB"""
    try:
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '')
        stock = request.form.get('stock', '')

        # Validaciones
        if not nombre:
            return redirect(url_for('index'))
        
        precio = float(precio)
        stock = int(stock)

        nuevo_producto = {
            'nombre': nombre,
            'precio': precio,
            'stock': stock,
            'creado_en': datetime.now()
        }

        resultado = productos_collection.insert_one(nuevo_producto)
        print(f"✓ Producto creado con ID: {resultado.inserted_id}")

    except ValueError:
        print("Error: Precio debe ser un número y Stock debe ser un entero")
    except Exception as e:
        print(f"Error al crear producto: {e}")

    return redirect(url_for('index'))

@app.route('/editar/<id>', methods=['POST'])
def editar(id):
    """Actualiza un producto existente"""
    try:
        # Validar que el ID sea un ObjectId válido
        if not ObjectId.is_valid(id):
            print(f"ID inválido: {id}")
            return redirect(url_for('index'))

        object_id = ObjectId(id)
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '')
        stock = request.form.get('stock', '')

        # Validaciones
        if not nombre:
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
            print(f"✓ Producto actualizado: {object_id}")
        else:
            print(f"✗ Producto no encontrado: {object_id}")

    except ValueError:
        print("Error: Precio debe ser un número y Stock debe ser un entero")
    except Exception as e:
        print(f"Error al editar producto: {e}")

    return redirect(url_for('index'))

@app.route('/eliminar/<id>', methods=['POST'])
def eliminar(id):
    """Elimina un producto por su ObjectId"""
    try:
        # Validar que el ID sea un ObjectId válido
        if not ObjectId.is_valid(id):
            print(f"ID inválido: {id}")
            return redirect(url_for('index'))

        object_id = ObjectId(id)
        resultado = productos_collection.delete_one({'_id': object_id})

        if resultado.deleted_count > 0:
            print(f"✓ Producto eliminado: {object_id}")
        else:
            print(f"✗ Producto no encontrado: {object_id}")

    except Exception as e:
        print(f"Error al eliminar producto: {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=puerto)
