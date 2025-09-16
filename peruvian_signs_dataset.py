import numpy as np
import json
import os

class PeruvianSignsDataset:
    """
    Dataset de señas del lenguaje de señas peruano.
    Almacena patrones de características para reconocimiento.
    """
    
    def __init__(self, dataset_file="signs_dataset.json"):
        """Inicializa el dataset de señas peruanas"""
        self.dataset_file = dataset_file
        self.signs_data = {}
        self._initialize_basic_signs()
        self.load_dataset()
    
    def _initialize_basic_signs(self):
        """Inicializa un conjunto básico de señas peruanas comunes"""
        # Patrones básicos aproximados (estos necesitarán ser calibrados con datos reales)
        self.basic_signs = {
            "HOLA": {
                "description": "Mano abierta, movimiento de saludo",
                "pattern": {
                    "fingers_extended": [True, True, True, True, True],  # Todos los dedos extendidos
                    "hand_openness": 0.8,  # Mano muy abierta
                    "confidence_threshold": 0.7
                }
            },
            
            "GRACIAS": {
                "description": "Mano hacia el pecho, dedos juntos",
                "pattern": {
                    "fingers_extended": [True, True, True, True, True],
                    "hand_openness": 0.3,  # Dedos juntos
                    "confidence_threshold": 0.7
                }
            },
            
            "SI": {
                "description": "Puño cerrado, movimiento de asentimiento",
                "pattern": {
                    "fingers_extended": [False, False, False, False, False],  # Puño cerrado
                    "hand_openness": 0.1,  # Muy cerrada
                    "confidence_threshold": 0.8
                }
            },
            
            "NO": {
                "description": "Índice extendido, movimiento lateral",
                "pattern": {
                    "fingers_extended": [False, True, False, False, False],  # Solo índice
                    "hand_openness": 0.2,
                    "confidence_threshold": 0.8
                }
            },
            
            "BIEN": {
                "description": "Pulgar arriba",
                "pattern": {
                    "fingers_extended": [True, False, False, False, False],  # Solo pulgar
                    "hand_openness": 0.2,
                    "confidence_threshold": 0.8
                }
            },
            
            "MAL": {
                "description": "Pulgar hacia abajo",
                "pattern": {
                    "fingers_extended": [True, False, False, False, False],  # Solo pulgar (orientación diferente)
                    "hand_openness": 0.2,
                    "confidence_threshold": 0.8,
                    "thumb_down": True
                }
            },
            
            "AMOR": {
                "description": "Índice y meñique extendidos (I Love You)",
                "pattern": {
                    "fingers_extended": [True, True, False, False, True],  # Pulgar, índice y meñique
                    "hand_openness": 0.4,
                    "confidence_threshold": 0.7
                }
            },
            
            "PAZ": {
                "description": "Índice y medio extendidos (V de victoria)",
                "pattern": {
                    "fingers_extended": [False, True, True, False, False],  # Índice y medio
                    "hand_openness": 0.3,
                    "confidence_threshold": 0.8
                }
            },
            
            "AGUA": {
                "description": "Mano formando copa",
                "pattern": {
                    "fingers_extended": [True, True, True, True, True],
                    "hand_openness": 0.5,  # Semi-curvada
                    "confidence_threshold": 0.6
                }
            },
            
            "COMIDA": {
                "description": "Dedos juntos hacia la boca",
                "pattern": {
                    "fingers_extended": [True, True, True, True, True],
                    "hand_openness": 0.2,  # Dedos muy juntos
                    "confidence_threshold": 0.7
                }
            }
        }
    
    def add_sign_pattern(self, sign_name, feature_vector, description=""):
        """
        Añade un nuevo patrón de seña al dataset
        
        Args:
            sign_name (str): Nombre de la seña
            feature_vector (np.array): Vector de características extraído
            description (str): Descripción opcional de la seña
        """
        if sign_name not in self.signs_data:
            self.signs_data[sign_name] = {
                "patterns": [],
                "description": description,
                "count": 0
            }
        
        # Convertir a lista para serialización JSON
        if isinstance(feature_vector, np.ndarray):
            feature_vector = feature_vector.tolist()
            
        self.signs_data[sign_name]["patterns"].append(feature_vector)
        self.signs_data[sign_name]["count"] += 1
        
        # Guardar automáticamente
        self.save_dataset()
    
    def get_sign_pattern(self, sign_name):
        """Obtiene el patrón promedio de una seña"""
        if sign_name not in self.signs_data or not self.signs_data[sign_name]["patterns"]:
            return None
            
        patterns = np.array(self.signs_data[sign_name]["patterns"])
        return np.mean(patterns, axis=0)
    
    def get_all_signs(self):
        """Retorna lista de todas las señas disponibles"""
        # Combinar señas básicas y señas aprendidas
        all_signs = list(self.basic_signs.keys())
        learned_signs = [name for name in self.signs_data.keys() if self.signs_data[name]["count"] > 0]
        
        return list(set(all_signs + learned_signs))
    
    def get_sign_info(self, sign_name):
        """Obtiene información detallada de una seña"""
        info = {}
        
        # Información de señas básicas
        if sign_name in self.basic_signs:
            info.update(self.basic_signs[sign_name])
            info["type"] = "basic"
        
        # Información de señas aprendidas
        if sign_name in self.signs_data and self.signs_data[sign_name]["count"] > 0:
            info.update({
                "learned_patterns": self.signs_data[sign_name]["count"],
                "average_pattern": self.get_sign_pattern(sign_name),
                "type": "learned"
            })
            
        return info if info else None
    
    def save_dataset(self):
        """Guarda el dataset en un archivo JSON"""
        try:
            with open(self.dataset_file, 'w', encoding='utf-8') as f:
                json.dump(self.signs_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar dataset: {e}")
    
    def load_dataset(self):
        """Carga el dataset desde un archivo JSON"""
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.signs_data.update(loaded_data)
            except Exception as e:
                print(f"Error al cargar dataset: {e}")
    
    def get_dataset_stats(self):
        """Retorna estadísticas del dataset"""
        stats = {
            "total_basic_signs": len(self.basic_signs),
            "total_learned_signs": len([k for k, v in self.signs_data.items() if v["count"] > 0]),
            "total_patterns": sum(v["count"] for v in self.signs_data.values()),
            "signs_by_pattern_count": {}
        }
        
        # Agrupar por número de patrones
        for sign, data in self.signs_data.items():
            count = data["count"]
            if count > 0:
                if count not in stats["signs_by_pattern_count"]:
                    stats["signs_by_pattern_count"][count] = []
                stats["signs_by_pattern_count"][count].append(sign)
        
        return stats
    
    def clear_sign(self, sign_name):
        """Elimina todos los patrones de una seña específica"""
        if sign_name in self.signs_data:
            self.signs_data[sign_name]["patterns"] = []
            self.signs_data[sign_name]["count"] = 0
            self.save_dataset()
            return True
        return False
    
    def export_dataset(self, export_file):
        """Exporta el dataset completo a un archivo"""
        export_data = {
            "basic_signs": self.basic_signs,
            "learned_signs": self.signs_data,
            "metadata": {
                "total_signs": len(self.get_all_signs()),
                "export_timestamp": "2024-01-01T00:00:00"
            }
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
