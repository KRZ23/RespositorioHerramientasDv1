#!/usr/bin/env blender -P
"""
Script de prueba: Visualiza landmarks 3D en Blender
Ejecutar con: blender -b -P scripts/blender/test_landmarks_visualization.py

Este script:
1. Lee los landmarks de una seña del dataset
2. Crea esferas en cada posición de landmark
3. Une las esferas con líneas (edges)
4. Renderiza y guarda la imagen
"""

import bpy
import sys
import os
from mathutils import Vector

# Agregar el proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Importar solo lo necesario (sin dependencias de OpenCV)
import json


# Conexiones entre landmarks de MediaPipe
HAND_CONNECTIONS = [
    # Pulgar
    (0, 1), (1, 2), (2, 3), (3, 4),
    # Índice
    (0, 5), (5, 6), (6, 7), (7, 8),
    # Medio
    (0, 9), (9, 10), (10, 11), (11, 12),
    # Anular
    (0, 13), (13, 14), (14, 15), (15, 16),
    # Meñique
    (0, 17), (17, 18), (18, 19), (19, 20),
    # Palma
    (5, 9), (9, 13), (13, 17)
]


def clear_scene():
    """Limpia toda la escena de Blender"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def setup_camera_and_lights():
    """Configura cámara e iluminación"""
    # Cámara
    bpy.ops.object.camera_add(location=(0, -1.5, 0.5))
    camera = bpy.context.object
    camera.rotation_euler = (1.3, 0, 0)  # Mirar hacia las manos
    bpy.context.scene.camera = camera
    
    # Luz principal (Key light)
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 3))
    sun = bpy.context.object
    sun.data.energy = 2.0
    
    # Luz de relleno (Fill light)
    bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
    area = bpy.context.object
    area.data.energy = 500
    
    # Configurar fondo
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.02, 0.02, 0.05, 1.0)  # Azul muy oscuro


def create_landmark_sphere(position, index, color=(0.3, 0.6, 1.0)):
    """Crea una esfera en la posición del landmark"""
    # Crear esfera
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.015,
        location=(position[0], position[2], -position[1])  # Convertir coords
    )
    sphere = bpy.context.object
    sphere.name = f"Landmark_{index}"
    
    # Crear material con color
    mat = bpy.data.materials.new(name=f"Material_Landmark_{index}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Roughness'].default_value = 0.4
    
    sphere.data.materials.append(mat)
    
    return sphere


def create_connection_cylinder(pos1, pos2, radius=0.005):
    """Crea un cilindro entre dos landmarks"""
    # Calcular dirección y longitud
    p1 = Vector((pos1[0], pos1[2], -pos1[1]))
    p2 = Vector((pos2[0], pos2[2], -pos2[1]))
    
    direction = p2 - p1
    length = direction.length
    center = (p1 + p2) / 2
    
    # Crear cilindro
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=center
    )
    cylinder = bpy.context.object
    
    # Rotar el cilindro para que apunte en la dirección correcta
    # El cilindro por defecto apunta en Z
    if length > 0:
        rot_quat = Vector((0, 0, 1)).rotation_difference(direction)
        cylinder.rotation_euler = rot_quat.to_euler()
    
    # Material gris oscuro
    mat = bpy.data.materials.new(name="Material_Connection")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.3, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.3
    
    cylinder.data.materials.append(mat)
    
    return cylinder


def visualize_hand_landmarks(landmarks_3d, hand_name="Hand"):
    """Visualiza los landmarks de una mano"""
    # Colores por dedo
    finger_colors = {
        'wrist': (0.5, 0.5, 0.5),      # Gris
        'thumb': (1.0, 0.3, 0.3),       # Rojo
        'index': (1.0, 0.7, 0.2),       # Naranja
        'middle': (0.3, 1.0, 0.3),      # Verde
        'ring': (0.3, 0.6, 1.0),        # Azul
        'pinky': (0.8, 0.3, 1.0)        # Morado
    }
    
    # Mapeo de índice a color
    landmark_colors = [finger_colors['wrist']]  # 0: muñeca
    landmark_colors.extend([finger_colors['thumb']] * 4)   # 1-4: pulgar
    landmark_colors.extend([finger_colors['index']] * 4)   # 5-8: índice
    landmark_colors.extend([finger_colors['middle']] * 4)  # 9-12: medio
    landmark_colors.extend([finger_colors['ring']] * 4)    # 13-16: anular
    landmark_colors.extend([finger_colors['pinky']] * 4)   # 17-20: meñique
    
    # Crear esferas para cada landmark
    spheres = []
    for i, pos in enumerate(landmarks_3d):
        sphere = create_landmark_sphere(pos, i, landmark_colors[i])
        spheres.append(sphere)
    
    # Crear conexiones (cilindros)
    for start_idx, end_idx in HAND_CONNECTIONS:
        pos1 = landmarks_3d[start_idx]
        pos2 = landmarks_3d[end_idx]
        create_connection_cylinder(pos1, pos2)
    
    return spheres


def render_scene(output_path="output/test_landmarks.png"):
    """Renderiza la escena"""
    scene = bpy.context.scene
    
    # Configurar render
    scene.render.engine = 'CYCLES'  # O 'BLENDER_EEVEE' para más rápido
    scene.cycles.samples = 128  # Calidad del render
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    
    # Renderizar
    bpy.ops.render.render(write_still=True)
    print(f"✅ Render guardado en: {output_path}")


def main():
    """Función principal"""
    print("🎨 Iniciando visualización de landmarks en Blender...")
    
    # Limpiar escena
    print("🧹 Limpiando escena...")
    clear_scene()
    
    # Configurar cámara y luces
    print("📷 Configurando cámara e iluminación...")
    setup_camera_and_lights()
    
    # Cargar landmarks del dataset directamente
    print("📊 Cargando landmarks del dataset...")
    dataset_path = os.path.join(project_root, "data/landmarks_3d_dataset.json")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Usar la seña "HOLA" como prueba
    sign_name = "HOLA"
    sign_data = dataset.get(sign_name)
    
    if sign_data is None:
        print(f"❌ Error: No se encontró la seña '{sign_name}'")
        return
    
    print(f"✨ Visualizando seña: {sign_name}")
    print(f"   Tipo: {sign_data['type']}")
    print(f"   Descripción: {sign_data['description']}")
    print(f"   Número de manos: {sign_data.get('num_hands', 1)}")
    
    # Obtener primer frame
    frames = sign_data['frames']
    first_frame = frames[0]
    
    # Visualizar landmarks
    print("🖐️ Creando visualización 3D...")
    
    if sign_data.get('num_hands', 1) == 2:
        # Dos manos
        print("   → Visualizando 2 manos")
        visualize_hand_landmarks(first_frame[0], "Hand_Left")
        visualize_hand_landmarks(first_frame[1], "Hand_Right")
    else:
        # Una mano
        print("   → Visualizando 1 mano")
        visualize_hand_landmarks(first_frame, "Hand")
    
    # Renderizar
    print("🎬 Renderizando imagen...")
    output_path = os.path.join(project_root, f"output/{sign_name}_blender.png")
    render_scene(output_path)
    
    print("✅ ¡Listo!")


if __name__ == "__main__":
    main()
