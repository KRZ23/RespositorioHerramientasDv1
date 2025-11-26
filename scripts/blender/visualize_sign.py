#!/usr/bin/env blender -P
"""
Visualiza cualquier seña del dataset en Blender
Uso: blender -b -P scripts/blender/visualize_sign.py -- NOMBRE_SEÑA
"""

import bpy
import sys
import os
from mathutils import Vector
import math
import json

# Obtener nombre de seña de argumentos
sign_name = "THUMBS_UP"  # Default
if "--" in sys.argv:
    args_after = sys.argv[sys.argv.index("--") + 1:]
    if args_after:
        sign_name = args_after[0].upper()

# Agregar proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Conexiones de mano
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),  # Índice
    (0, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (0, 13), (13, 14), (14, 15), (15, 16),  # Anular
    (0, 17), (17, 18), (18, 19), (19, 20),  # Meñique
    (5, 9), (9, 13), (13, 17)  # Palma
]


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_glowing_sphere(position, index, color=(1, 0.3, 0.3), radius=0.04):
    """Crea esfera brillante"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=position)
    sphere = bpy.context.object
    sphere.name = f"Landmark_{index}"
    
    mat = bpy.data.materials.new(name=f"Mat_{index}")
    mat.node_tree.nodes.clear()
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = 3.0
    
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs[0], output.inputs[0])
    
    sphere.data.materials.append(mat)
    return sphere


def create_glowing_cylinder(pos1, pos2, radius=0.015, color=(0.8, 0.8, 1.0)):
    """Crea cilindro brillante"""
    p1 = Vector(pos1)
    p2 = Vector(pos2)
    
    direction = p2 - p1
    length = direction.length
    
    if length < 0.001:
        return None
    
    center = (p1 + p2) / 2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=center)
    cylinder = bpy.context.object
    
    rot_quat = Vector((0, 0, 1)).rotation_difference(direction)
    cylinder.rotation_euler = rot_quat.to_euler()
    
    mat = bpy.data.materials.new(name="Mat_Connection")
    mat.node_tree.nodes.clear()
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = 1.5
    
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs[0], output.inputs[0])
    
    cylinder.data.materials.append(mat)
    return cylinder


def convert_coords(landmarks, scale=5.0):
    """Convierte MediaPipe a Blender con escala"""
    converted = []
    for p in landmarks:
        # MediaPipe: X derecha, Y abajo, Z hacia cámara
        # Blender: X derecha, Y adelante, Z arriba
        x = (p[0] - 0.5) * scale  # Centrar en X
        y = -p[2] * scale  # Z de MP → -Y de Blender (profundidad)
        z = (0.5 - p[1]) * scale  # Y de MP → Z de Blender (altura invertida)
        converted.append((x, y, z))
    return converted


def visualize_hand(landmarks):
    """Visualiza mano con colores"""
    blender_coords = convert_coords(landmarks)
    
    # Colores por dedo
    colors = {
        'wrist': (0.9, 0.9, 0.9),
        'thumb': (1.0, 0.2, 0.2),
        'index': (1.0, 0.6, 0.0),
        'middle': (0.2, 1.0, 0.2),
        'ring': (0.2, 0.6, 1.0),
        'pinky': (1.0, 0.2, 1.0)
    }
    
    landmark_colors = [colors['wrist']]
    landmark_colors.extend([colors['thumb']] * 4)
    landmark_colors.extend([colors['index']] * 4)
    landmark_colors.extend([colors['middle']] * 4)
    landmark_colors.extend([colors['ring']] * 4)
    landmark_colors.extend([colors['pinky']] * 4)
    
    # Crear esferas
    for i, pos in enumerate(blender_coords):
        radius = 0.08 if i == 0 else 0.05
        create_glowing_sphere(pos, i, landmark_colors[i], radius)
    
    # Crear conexiones
    for start, end in HAND_CONNECTIONS:
        create_glowing_cylinder(blender_coords[start], blender_coords[end])
    
    return blender_coords


def setup_scene(hand_center):
    """Configura cámara y luces"""
    # Cámara
    bpy.ops.object.camera_add(location=(hand_center[0], hand_center[1] - 8, hand_center[2]))
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = camera
    
    # Luces
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 5))
    bpy.context.object.data.energy = 8.0
    
    bpy.ops.object.light_add(type='AREA', location=(0, -5, 2))
    bpy.context.object.data.energy = 1500
    
    # Mundo
    world = bpy.context.scene.world
    if world.node_tree:
        world.node_tree.nodes.clear()
    bg = world.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (0.05, 0.08, 0.12, 1.0)
    bg.inputs['Strength'].default_value = 0.8
    output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(bg.outputs[0], output.inputs[0])


def main():
    print("\n" + "="*80)
    print(f"🎨 VISUALIZANDO SEÑA: {sign_name}")
    print("="*80 + "\n")
    
    clear_scene()
    
    # Cargar dataset
    dataset_path = os.path.join(project_root, "data/landmarks_3d_dataset.json")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    if sign_name not in dataset:
        print(f"❌ Error: Seña '{sign_name}' no encontrada en el dataset")
        print(f"\nSeñas disponibles:")
        for name in sorted(dataset.keys()):
            print(f"  - {name}")
        return
    
    sign_data = dataset[sign_name]
    landmarks = sign_data['frames'][0]
    
    print(f"✨ Seña: {sign_name}")
    print(f"   Tipo: {sign_data['type']}")
    print(f"   Descripción: {sign_data.get('description', 'N/A')}")
    
    # Analizar profundidad
    z_values = [p[2] for p in landmarks]
    print(f"\n📊 Análisis de profundidad (Z):")
    print(f"   Min: {min(z_values):.4f}")
    print(f"   Max: {max(z_values):.4f}")
    print(f"   Rango: {max(z_values) - min(z_values):.4f}")
    
    if max(z_values) - min(z_values) < 0.02:
        print("   ⚠️ ADVERTENCIA: Datos casi planos, puede ser una migración aproximada")
    else:
        print("   ✅ Buenos datos 3D con profundidad real")
    
    print("\n🖐️ Creando visualización...")
    coords = visualize_hand(landmarks)
    
    # Calcular centro
    import numpy as np
    center = np.array(coords).mean(axis=0)
    
    print("📷 Configurando escena...")
    setup_scene(center)
    
    # Renderizar
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    
    output_path = os.path.join(project_root, f"output/{sign_name}_3D.png")
    scene.render.filepath = output_path
    
    print(f"\n🎬 Renderizando: {output_path}")
    bpy.ops.render.render(write_still=True)
    
    print("\n" + "="*80)
    print("✅ ¡COMPLETADO!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
