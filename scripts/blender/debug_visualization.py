#!/usr/bin/env blender -P
"""
Script de DEPURACIÓN: Muestra landmarks con vista automática
"""

import bpy
import sys
import os
from mathutils import Vector
import math
import json

# Agregar proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def clear_scene():
    """Limpia la escena"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_simple_sphere(position, radius=0.1, color=(1, 0, 0)):
    """Crea una esfera simple y visible"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=position
    )
    sphere = bpy.context.object
    
    # Material simple
    mat = bpy.data.materials.new(name="SimpleMat")
    sphere.data.materials.append(mat)
    
    return sphere


def main():
    print("\n" + "="*80)
    print("🔍 MODO DEPURACIÓN - Visualización Simple")
    print("="*80 + "\n")
    
    # Limpiar
    clear_scene()
    
    # Cargar datos
    dataset_path = os.path.join(project_root, "data/landmarks_3d_dataset.json")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    sign_data = dataset.get("HOLA")
    landmarks = sign_data['frames'][0]
    
    print(f"📊 Landmarks cargados: {len(landmarks)} puntos\n")
    print("Primeros 5 landmarks (MediaPipe coords):")
    for i in range(min(5, len(landmarks))):
        print(f"  [{i}] x={landmarks[i][0]:.4f}, y={landmarks[i][1]:.4f}, z={landmarks[i][2]:.4f}")
    
    # Encontrar centro y rango
    import numpy as np
    landmarks_array = np.array(landmarks)
    center = landmarks_array.mean(axis=0)
    min_coords = landmarks_array.min(axis=0)
    max_coords = landmarks_array.max(axis=0)
    
    print(f"\n📍 Centro: x={center[0]:.4f}, y={center[1]:.4f}, z={center[2]:.4f}")
    print(f"📏 Rango X: {min_coords[0]:.4f} a {max_coords[0]:.4f}")
    print(f"📏 Rango Y: {min_coords[1]:.4f} a {max_coords[1]:.4f}")
    print(f"📏 Rango Z: {min_coords[2]:.4f} a {max_coords[2]:.4f}")
    
    # Crear esferas GRANDES Y ROJAS en posiciones originales (sin conversión)
    print("\n🎨 Creando esferas en posiciones originales...")
    
    for i, pos in enumerate(landmarks):
        # Usar coordenadas directamente, solo escalar
        x = pos[0] * 10  # Escalar X10 para hacer visible
        y = pos[1] * 10
        z = pos[2] * 10
        
        create_simple_sphere(
            position=(x, y, z),
            radius=0.3,  # Esfera GRANDE
            color=(1, 0, 0)  # Rojo
        )
        
        if i == 0:
            print(f"  Primera esfera en: ({x:.2f}, {y:.2f}, {z:.2f})")
    
    print(f"✅ Creadas {len(landmarks)} esferas")
    
    # Configurar cámara para ver TODO
    print("\n📷 Configurando cámara...")
    
    # Calcular centro en coordenadas escaladas
    center_scaled = center * 10
    
    bpy.ops.object.camera_add(
        location=(center_scaled[0], center_scaled[1] - 15, center_scaled[2])
    )
    camera = bpy.context.object
    camera.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = camera
    
    print(f"  Cámara en: ({center_scaled[0]:.2f}, {center_scaled[1]-15:.2f}, {center_scaled[2]:.2f})")
    
    # LUZ MUY BRILLANTE
    print("\n💡 Agregando luz intensa...")
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
    sun = bpy.context.object
    sun.data.energy = 10.0  # MUY BRILLANTE
    
    # Fondo BLANCO
    world = bpy.context.scene.world
    if world.node_tree:
        world.node_tree.nodes.clear()
    bg = world.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (1, 1, 1, 1)  # BLANCO
    bg.inputs['Strength'].default_value = 3.0
    output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(bg.outputs[0], output.inputs[0])
    
    # Renderizar
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'  # Motor más simple
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.display.shading.light = 'MATCAP'
    
    output_path = os.path.join(project_root, "output/DEBUG_landmarks.png")
    scene.render.filepath = output_path
    
    print(f"\n🎬 Renderizando a: {output_path}")
    bpy.ops.render.render(write_still=True)
    
    print("\n" + "="*80)
    print("✅ ¡COMPLETADO!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
