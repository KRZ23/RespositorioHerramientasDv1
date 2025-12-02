"""
Script de Prueba para Modelo Rigeado en Blender

INSTRUCCIONES:
1. Abre Blender y carga tu modelo rigeado
2. Ve a Scripting workspace (arriba, junto a Modeling, Shading, etc.)
3. Crea un nuevo script (Text > New)
4. Copia COMPLETO este archivo
5. Pega en el editor de texto
6. Presiona Alt+P o click en ▶ Run Script
"""

import bpy
import math

# =========================================================================
# CONFIGURACIÓN
# =========================================================================

# Nombre del armature/rig (ajustar si es necesario)
ARMATURE_NAME = None  # Si es None, usa el primer armature que encuentre

# Duración de la animación (frames)
ANIMATION_LENGTH = 120
FPS = 24

# =========================================================================
# FUNCIONES AUXILIARES
# =========================================================================

def get_armature():
    """Encuentra el armature en la escena"""
    if ARMATURE_NAME:
        return bpy.data.objects.get(ARMATURE_NAME)
    
    # Buscar primer armature
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


def list_bones(armature):
    """Lista todos los huesos del rig"""
    if not armature:
        return []
    
    bones = []
    for bone in armature.pose.bones:
        bones.append(bone.name)
    return bones


def find_hand_bones(armature):
    """Intenta encontrar huesos de las manos"""
    if not armature:
        return {"left": [], "right": []}
    
    hand_bones = {"left": [], "right": []}
    
    keywords_left = ['left', 'l_', '.l', '_l', 'izquierda', 'hand.l']
    keywords_right = ['right', 'r_', '.r', '_r', 'derecha', 'hand.r']
    keywords_hand = ['hand', 'mano', 'finger', 'dedo', 'thumb', 'pulgar', 
                     'index', 'indice', 'middle', 'medio', 'ring', 'anular', 
                     'pinky', 'menique']
    
    for bone in armature.pose.bones:
        name_lower = bone.name.lower()
        
        # Verificar si es un hueso de mano
        is_hand_bone = any(kw in name_lower for kw in keywords_hand)
        
        if is_hand_bone:
            if any(kw in name_lower for kw in keywords_left):
                hand_bones["left"].append(bone.name)
            elif any(kw in name_lower for kw in keywords_right):
                hand_bones["right"].append(bone.name)
    
    return hand_bones


def animate_bone_rotation(armature, bone_name, start_frame, end_frame, axis='Z', amplitude=0.5):
    """Anima la rotación de un hueso"""
    if bone_name not in armature.pose.bones:
        return False
    
    bone = armature.pose.bones[bone_name]
    
    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        
        # Calcular rotación sinusoidal
        progress = (frame - start_frame) / (end_frame - start_frame)
        angle = math.sin(progress * math.pi * 2) * amplitude
        
        # Aplicar rotación según eje
        if axis == 'X':
            bone.rotation_euler[0] = angle
        elif axis == 'Y':
            bone.rotation_euler[1] = angle
        else:  # Z
            bone.rotation_euler[2] = angle
        
        # Insertar keyframe
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    return True


def animate_bone_location(armature, bone_name, start_frame, end_frame, axis='Z', amplitude=0.1):
    """Anima la posición de un hueso"""
    if bone_name not in armature.pose.bones:
        return False
    
    bone = armature.pose.bones[bone_name]
    
    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        
        # Calcular movimiento sinusoidal
        progress = (frame - start_frame) / (end_frame - start_frame)
        offset = math.sin(progress * math.pi * 2) * amplitude
        
        # Aplicar movimiento según eje
        if axis == 'X':
            bone.location[0] = offset
        elif axis == 'Y':
            bone.location[1] = offset
        else:  # Z
            bone.location[2] = offset
        
        # Insertar keyframe
        bone.keyframe_insert(data_path="location", frame=frame)
    
    return True


# =========================================================================
# SCRIPT PRINCIPAL
# =========================================================================

def main():
    print("\n" + "="*70)
    print("🎬 SCRIPT DE PRUEBA PARA MODELO RIGEADO")
    print("="*70 + "\n")
    
    # Encontrar armature
    armature = get_armature()
    
    if not armature:
        print("❌ ERROR: No se encontró ningún armature en la escena")
        print("\nModelos disponibles:")
        for obj in bpy.data.objects:
            print(f"  • {obj.name} (tipo: {obj.type})")
        return
    
    print(f"✅ Armature encontrado: {armature.name}\n")
    
    # Listar huesos
    bones = list_bones(armature)
    print(f"📋 Total de huesos: {len(bones)}\n")
    
    if len(bones) == 0:
        print("❌ ERROR: El armature no tiene huesos")
        return
    
    # Mostrar primeros 20 huesos
    print("Huesos principales:")
    for i, bone_name in enumerate(bones[:20], 1):
        print(f"  {i:2d}. {bone_name}")
    
    if len(bones) > 20:
        print(f"  ... y {len(bones) - 20} más")
    
    # Buscar huesos de manos
    print("\n🔍 Buscando huesos de manos...")
    hand_bones = find_hand_bones(armature)
    
    if hand_bones["left"]:
        print(f"\n👈 Huesos mano izquierda ({len(hand_bones['left'])}):")
        for bone in hand_bones["left"][:10]:
            print(f"  • {bone}")
    
    if hand_bones["right"]:
        print(f"\n👉 Huesos mano derecha ({len(hand_bones['right'])}):")
        for bone in hand_bones["right"][:10]:
            print(f"  • {bone}")
    
    # Configurar escena
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = ANIMATION_LENGTH
    bpy.context.scene.render.fps = FPS
    
    # Asegurar que estamos en Object Mode primero
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Seleccionar armature
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    # Modo pose
    bpy.ops.object.mode_set(mode='POSE')
    
    # Limpiar animaciones anteriores
    if armature.animation_data:
        armature.animation_data_clear()
    
    print(f"\n🎬 Generando animación de prueba...")
    print(f"   Frames: 1-{ANIMATION_LENGTH}")
    
    # ANIMACIÓN DE PRUEBA: Animar los primeros huesos encontrados
    animated_count = 0
    
    # Intentar animar hueso raíz o principal
    root_keywords = ['root', 'hips', 'pelvis', 'spine', 'cadera', 'columna']
    root_bone = None
    
    for bone_name in bones:
        if any(kw in bone_name.lower() for kw in root_keywords):
            root_bone = bone_name
            break
    
    if root_bone:
        print(f"\n   ↕️  Animando movimiento vertical: {root_bone}")
        animate_bone_location(armature, root_bone, 1, ANIMATION_LENGTH, 'Z', 0.05)
        animated_count += 1
    
    # Animar huesos de manos si se encontraron
    if hand_bones["left"]:
        bone_name = hand_bones["left"][0]
        print(f"   🔄 Animando rotación: {bone_name}")
        animate_bone_rotation(armature, bone_name, 1, ANIMATION_LENGTH, 'Z', 0.3)
        animated_count += 1
    
    if hand_bones["right"]:
        bone_name = hand_bones["right"][0]
        print(f"   🔄 Animando rotación: {bone_name}")
        animate_bone_rotation(armature, bone_name, 1, ANIMATION_LENGTH, 'Z', -0.3)
        animated_count += 1
    
    # Si no se encontraron manos, animar algunos huesos al azar
    if animated_count < 3:
        for i, bone_name in enumerate(bones[:5]):
            if i >= 3:
                break
            print(f"   🔄 Animando: {bone_name}")
            animate_bone_rotation(armature, bone_name, 1, ANIMATION_LENGTH, 'Z', 0.2)
            animated_count += 1
    
    # Volver a frame 1
    bpy.context.scene.frame_set(1)
    
    print(f"\n✅ ANIMACIÓN CREADA")
    print(f"   Huesos animados: {animated_count}")
    print(f"   Duración: {ANIMATION_LENGTH} frames ({ANIMATION_LENGTH/FPS:.1f} segundos)")
    print("\n" + "="*70)
    print("▶️  Presiona ESPACIO para reproducir la animación")
    print("="*70 + "\n")


# =========================================================================
# EJECUTAR
# =========================================================================

if __name__ == "__main__":
    main()


# =========================================================================
# FUNCIONES EXTRAS (para usar después)
# =========================================================================

def animate_custom_bone(bone_name, frames=120):
    """
    Función helper para animar un hueso específico
    Uso: animate_custom_bone("Hand.L", 60)
    """
    armature = get_armature()
    if not armature:
        print("❌ No se encontró armature")
        return
    
    bpy.ops.object.mode_set(mode='POSE')
    animate_bone_rotation(armature, bone_name, 1, frames, 'Z', 0.5)
    print(f"✅ {bone_name} animado")


def list_all_bones():
    """Lista todos los huesos disponibles"""
    armature = get_armature()
    if not armature:
        print("❌ No se encontró armature")
        return
    
    bones = list_bones(armature)
    print(f"\n📋 Total: {len(bones)} huesos\n")
    for i, bone in enumerate(bones, 1):
        print(f"{i:3d}. {bone}")


def clear_animation():
    """Limpia toda la animación del armature"""
    armature = get_armature()
    if armature and armature.animation_data:
        armature.animation_data_clear()
        print("✅ Animación limpiada")
    else:
        print("ℹ️  No hay animación para limpiar")


# Mostrar ayuda
print("\n💡 FUNCIONES DISPONIBLES:")
print("   • list_all_bones()           - Lista todos los huesos")
print("   • animate_custom_bone(name)  - Anima un hueso específico")
print("   • clear_animation()          - Limpia la animación")
print("   • main()                     - Ejecuta el script completo\n")
