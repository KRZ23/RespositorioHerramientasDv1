#!/usr/bin/env blender -P
"""
Script mejorado: Visualiza landmarks 3D en Blender con mejor iluminación
Ejecutar con: blender -b -P scripts/blender/visualize_landmarks_fixed.py
"""

import bpy
import sys
import os
from mathutils import Vector
import math

# Agregar el proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

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
    # Seleccionar todos los objetos
    bpy.ops.object.select_all(action='SELECT')
    # Eliminar
    bpy.ops.object.delete(use_global=False)
    
    # Limpiar datos huérfanos
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def setup_camera_and_lights():
    """Configura cámara e iluminación mejorada"""
    
    # === CÁMARA ===
    bpy.ops.object.camera_add(location=(0, -1.5, 0))
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(90), 0, 0)  # Mirar hacia adelante
    bpy.context.scene.camera = camera
    
    # Ajustar distancia focal para ver mejor
    camera.data.lens = 50
    
    # === LUCES ===
    
    # Luz principal fuerte (Key light)
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 3))
    sun = bpy.context.object
    sun.data.energy = 5.0  # Más potencia
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Luz de relleno frontal
    bpy.ops.object.light_add(type='AREA', location=(0, -2, 1))
    area1 = bpy.context.object
    area1.data.energy = 1000  # Muy brillante
    area1.data.size = 2
    area1.rotation_euler = (math.radians(90), 0, 0)
    
    # Luz trasera (Rim light)
    bpy.ops.object.light_add(type='POINT', location=(0, 1, 0.5))
    point = bpy.context.object
    point.data.energy = 500
    
    # === MUNDO (Ambiente) ===
    world = bpy.context.scene.world
    if world.node_tree is None:
        world.node_tree = bpy.data.node_groups.new('WorldNodeTree', 'ShaderNodeTree')
    
    # Limpiar nodos existentes
    world.node_tree.nodes.clear()
    
    # Crear fondo blanco brillante
    bg_node = world.node_tree.nodes.new('ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = (0.8, 0.85, 0.9, 1.0)  # Azul claro
    bg_node.inputs['Strength'].default_value = 1.5  # Muy brillante
    
    output_node = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])


def create_landmark_sphere(position, index, color=(0.3, 0.6, 1.0), radius=0.03):
    """Crea una esfera emisiva en la posición del landmark"""
    
    # Crear esfera
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=position
    )
    sphere = bpy.context.object
    sphere.name = f"Landmark_{index}"
    
    # Crear material EMISIVO (brilla por sí mismo)
    mat = bpy.data.materials.new(name=f"Mat_Landmark_{index}")
    mat.node_tree.nodes.clear()
    
    # Nodos
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Emission shader (para que brille)
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = 2.0  # Brillo fuerte
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    sphere.data.materials.append(mat)
    
    return sphere


def create_connection_cylinder(pos1, pos2, radius=0.01, color=(0.9, 0.9, 0.95)):
    """Crea un cilindro brillante entre dos landmarks"""
    
    p1 = Vector(pos1)
    p2 = Vector(pos2)
    
    direction = p2 - p1
    length = direction.length
    
    if length < 0.001:  # Evitar cilindros de longitud cero
        return None
    
    center = (p1 + p2) / 2
    
    # Crear cilindro
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=center
    )
    cylinder = bpy.context.object
    
    # Rotar el cilindro
    rot_quat = Vector((0, 0, 1)).rotation_difference(direction)
    cylinder.rotation_euler = rot_quat.to_euler()
    
    # Material emisivo para las conexiones
    mat = bpy.data.materials.new(name="Mat_Connection")
    mat.node_tree.nodes.clear()
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = 1.0
    
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    cylinder.data.materials.append(mat)
    
    return cylinder


def convert_mediapipe_to_blender(landmarks_3d, scale=2.0):
    """
    Convierte coordenadas de MediaPipe a Blender
    MediaPipe: X derecha, Y abajo, Z hacia cámara (0-1 normalizado)
    Blender: X derecha, Y adelante, Z arriba
    """
    converted = []
    for point in landmarks_3d:
        x = point[0] * scale  # X se mantiene
        y = -point[2] * scale  # Z de MediaPipe → -Y de Blender (profundidad)
        z = -point[1] * scale  # Y de MediaPipe → -Z de Blender (invertir altura)
        converted.append((x, y, z))
    return converted


def visualize_hand_landmarks(landmarks_3d):
    """Visualiza los landmarks de una mano"""
    
    # Convertir coordenadas
    blender_coords = convert_mediapipe_to_blender(landmarks_3d, scale=3.0)
    
    # Colores por dedo (más brillantes)
    finger_colors = {
        'wrist': (0.8, 0.8, 0.8),      # Gris claro
        'thumb': (1.0, 0.2, 0.2),       # Rojo brillante
        'index': (1.0, 0.6, 0.0),       # Naranja
        'middle': (0.2, 1.0, 0.2),      # Verde brillante
        'ring': (0.2, 0.6, 1.0),        # Azul
        'pinky': (1.0, 0.2, 1.0)        # Magenta
    }
    
    # Mapeo de índice a color
    landmark_colors = [finger_colors['wrist']]  # 0: muñeca
    landmark_colors.extend([finger_colors['thumb']] * 4)   # 1-4
    landmark_colors.extend([finger_colors['index']] * 4)   # 5-8
    landmark_colors.extend([finger_colors['middle']] * 4)  # 9-12
    landmark_colors.extend([finger_colors['ring']] * 4)    # 13-16
    landmark_colors.extend([finger_colors['pinky']] * 4)   # 17-20
    
    # Crear esferas MÁS GRANDES
    spheres = []
    for i, pos in enumerate(blender_coords):
        # Muñeca más grande
        radius = 0.06 if i == 0 else 0.04
        sphere = create_landmark_sphere(pos, i, landmark_colors[i], radius)
        spheres.append(sphere)
    
    # Crear conexiones
    for start_idx, end_idx in HAND_CONNECTIONS:
        pos1 = blender_coords[start_idx]
        pos2 = blender_coords[end_idx]
        create_connection_cylinder(pos1, pos2, radius=0.015)
    
    print(f"✅ Creados {len(spheres)} landmarks y {len(HAND_CONNECTIONS)} conexiones")
    
    return spheres


def setup_render_settings(output_path):
    """Configura el motor de render"""
    scene = bpy.context.scene
    
    # Usar EEVEE (más rápido y brillante)
    scene.render.engine = 'BLENDER_EEVEE'  # Motor de render
    
    # Configuraciones básicas de EEVEE
    # (Blender 5.0 cambió algunas propiedades)
    
    # Resolución
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Formato
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    
    # Fondo transparente
    scene.render.film_transparent = False


def render_scene(output_path):
    """Renderiza la escena"""
    setup_render_settings(output_path)
    
    print("🎬 Renderizando...")
    bpy.ops.render.render(write_still=True)
    print(f"✅ Render guardado en: {output_path}")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🎨 VISUALIZACIÓN MEJORADA DE LANDMARKS EN BLENDER")
    print("="*60 + "\n")
    
    # Limpiar escena
    print("🧹 Limpiando escena...")
    clear_scene()
    
    # Configurar cámara y luces
    print("📷 Configurando cámara e iluminación mejorada...")
    setup_camera_and_lights()
    
    # Cargar landmarks
    print("📊 Cargando landmarks del dataset...")
    dataset_path = os.path.join(project_root, "data/landmarks_3d_dataset.json")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Usar la seña "HOLA"
    sign_name = "HOLA"
    sign_data = dataset.get(sign_name)
    
    if sign_data is None:
        print(f"❌ Error: No se encontró la seña '{sign_name}'")
        return
    
    print(f"\n✨ Visualizando seña: {sign_name}")
    print(f"   Tipo: {sign_data['type']}")
    print(f"   Descripción: {sign_data['description']}")
    print(f"   Número de manos: {sign_data.get('num_hands', 1)}\n")
    
    # Obtener primer frame
    frames = sign_data['frames']
    first_frame = frames[0]
    
    # Visualizar landmarks
    print("🖐️ Creando visualización 3D...")
    
    if sign_data.get('num_hands', 1) == 2:
        print("   → Visualizando 2 manos")
        visualize_hand_landmarks(first_frame[0])
        # TODO: Agregar segunda mano con offset
    else:
        print("   → Visualizando 1 mano")
        visualize_hand_landmarks(first_frame)
    
    # Renderizar
    output_path = os.path.join(project_root, f"output/{sign_name}_blender_fixed.png")
    print(f"\n🎬 Renderizando a: {output_path}")
    render_scene(output_path)
    
    print("\n" + "="*60)
    print("✅ ¡COMPLETADO!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
