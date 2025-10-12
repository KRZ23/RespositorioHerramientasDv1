# 🤟 Hola - Traducción de Lenguaje de Señas

Una aplicación web moderna para traducción de lenguaje de señas en tiempo real usando MediaPipe y tecnología de IA.

## 🚀 Características

- **Traducción en Tiempo Real**: Interpreta señas instantáneamente con precisión
- **Detección de Poses y Manos**: Usa MediaPipe para detección precisa de gestos
- **Interface Moderna**: Diseño limpio y responsivo con Tailwind CSS
- **Workers Optimizados**: Procesamiento en segundo plano para mejor rendimiento
- **Demo Interactiva**: Prueba la funcionalidad directamente en el navegador

## 🛠️ Tecnologías

- **Framework**: Next.js 15.5.4 con Turbopack
- **Frontend**: React 19, TypeScript
- **Estilos**: Tailwind CSS v4
- **IA/ML**: MediaPipe Tasks Vision, ONNX Runtime Web
- **Estado**: Zustand
- **Iconos**: Lucide React

## 📦 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/KRZ23/RespositorioHerramientasDv1.git
cd hola
```

2. Instala las dependencias:
```bash
npm install
```

3. Ejecuta el servidor de desarrollo:
```bash
npm run dev
```

4. Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## 🎯 Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo con Turbopack
- `npm run build` - Construye la aplicación para producción
- `npm run start` - Inicia el servidor de producción
- `npm run lint` - Ejecuta ESLint para verificar código

## 🏗️ Estructura del Proyecto

```
src/
├── app/                    # App Router de Next.js
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página de inicio
│   └── demo/
│       └── page.tsx       # Página de demo interactiva
├── components/            # Componentes reutilizables
│   ├── ui/                # Componentes base
│   ├── navbar.tsx         # Barra de navegación
│   ├── hero.tsx           # Sección héroe
│   ├── features.tsx       # Características
│   ├── steps.tsx          # Pasos de uso
│   ├── cta.tsx           # Call to action
│   └── footer.tsx        # Pie de página
├── lib/                   # Utilidades y tipos
│   ├── types.ts          # Definiciones de tipos
│   └── utils.ts          # Funciones utilitarias
├── workers/              # Web Workers para procesamiento
│   ├── infer.worker.ts   # Worker de inferencia heurística
│   └── keypoints.worker.ts # Worker de extracción de keypoints
└── styles/
    └── globals.css       # Estilos globales
```

## 🎮 Uso de la Demo

1. Ve a `/demo` en la aplicación
2. Haz clic en "Activar cámara" para comenzar
3. Realiza los siguientes gestos frente a la cámara:
   - **HOLA**: Mano oscilando (oleada)
   - **SÍ**: Pulgar arriba
   - **NO**: Índice oscilando lateralmente
   - **GRACIAS**: Mano cerca de la boca y luego alejándose

## 🔧 Configuración

### MediaPipe
La aplicación usa MediaPipe para detección de poses y manos. Los modelos se cargan automáticamente desde CDN.

### Workers
- `infer.worker.ts`: Procesa los datos de keypoints y realiza inferencia heurística
- `keypoints.worker.ts`: Extrae keypoints de MediaPipe (actualmente no usado en demo)

### Tipos TypeScript
Todos los tipos están definidos en `src/lib/types.ts` para consistencia.

## 🚨 Solución de Problemas

### Error "Module not found"
- Verifica que todos los archivos componentes existan
- Asegúrate de que los exports por defecto estén correctos
- Revisa el path mapping en `tsconfig.json`

### Errores de MediaPipe
- Verifica permisos de cámara en el navegador
- Asegúrate de que la aplicación se ejecute en HTTPS en producción
- Los modelos de MediaPipe se cargan desde CDN automáticamente

### Errores de TypeScript
- Ejecuta `npm run lint` para verificar errores
- Revisa que no haya tipos `any` no permitidos
- Verifica las referencias de workers

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- **Equipo de Desarrollo** - *Trabajo inicial* - [KRZ23](https://github.com/KRZ23)

---

**¡Hola** está diseñado para hacer la comunicación más inclusiva y accesible para todos! 🌟
