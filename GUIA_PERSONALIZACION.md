# 🎨 Academia Musical - Guía de Personalización del Diseño

## 📁 Estructura de Archivos de Diseño CAMBIO ACTUAL

```
academiaMusical/
├── usuarios/templates/usuarios/
│   ├── base.html                    # 🏗️ Template base con sidebar y layout principal
│   ├── admin_dashboard.html         # 📊 Dashboard principal
│   ├── admin_estudiantes.html       # 👥 Gestión de estudiantes
│   └── ...otros archivos admin
└── static/css/
    └── admin-enhancement.css        # ✨ Estilos avanzados y mejoras
```

## 🎨 Personalización Rápida de Colores

### 1. Cambiar Colores Principales
**Archivo:** `base.html` (líneas 15-19)

```css
:root {
  --primary-color: #667eea;        /* 🔵 Color principal */
  --primary-dark: #5a67d8;         /* 🔷 Versión oscura */
  --secondary-color: #764ba2;      /* 🟣 Color secundario */
}
```

**Ejemplos de paletas:**
- **Verde:** `#10b981` y `#059669`
- **Rojo:** `#ef4444` y `#dc2626`
- **Naranja:** `#f59e0b` y `#d97706`
- **Morado:** `#8b5cf6` y `#7c3aed`

### 2. Cambiar Gradientes
**Archivo:** `admin-enhancement.css` (líneas 15-20)

```css
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 📏 Personalización de Dimensiones

### 1. Ancho del Sidebar
**Archivo:** `base.html` (línea 22)

```css
--sidebar-width: 280px;  /* Cambiar a 320px para más ancho, 240px para más estrecho */
```

### 2. Tamaños de Texto
**Archivo:** `base.html`

```css
.sidebar-header .logo {
  font-size: 1.5rem;     /* Tamaño del título del sidebar */
}

.content-header h1 {
  font-size: 1.875rem;   /* Tamaño del título principal */
}
```

## 🎭 Personalización de Efectos Visuales

### 1. Sombras
**Archivo:** `base.html` (líneas 26-28)

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);    /* Sombra suave */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);   /* Sombra media */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1); /* Sombra fuerte */
```

### 2. Velocidades de Animación
**Archivo:** `base.html`

```css
transition: all 0.3s ease;  /* Cambiar 0.3s por 0.2s (más rápido) o 0.5s (más lento) */
```

### 3. Efectos Hover
**Archivo:** `base.html` (línea 120)

```css
.sidebar-nav .nav-link:hover {
  transform: translateX(4px);  /* Cambiar 4px por 2px (menos) o 8px (más) */
}
```

## 🌈 Personalización de Fondos

### 1. Fondo del Sidebar
**Archivo:** `base.html` (línea 46)

```css
background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
```

**Alternativas:**
- **Sólido:** `background: #667eea;`
- **Degradado vertical:** `linear-gradient(180deg, ...)`
- **Con imagen:** `linear-gradient(...), url('imagen.jpg')`

### 2. Fondo General
**Archivo:** `base.html` (línea 25)

```css
--bg-light: #f8fafc;  /* Cambiar por #ffffff (blanco) o #f3f4f6 (gris más claro) */
```

## 📐 Personalización de Formas

### 1. Redondez de Elementos
**Archivo:** `base.html`

```css
border-radius: 1rem;     /* Tarjetas - cambiar por 0.5rem (menos) o 1.5rem (más) */
border-radius: 0.75rem;  /* Botones - personalizar según gusto */
```

### 2. Espaciado
**Archivo:** `base.html`

```css
padding: 2rem;           /* Contenido - cambiar por 1.5rem o 2.5rem */
margin-bottom: 2rem;     /* Separación entre elementos */
```

## 🔧 Personalización Avanzada

### 1. Agregar Nuevos Colores
**Archivo:** `base.html` (después de línea 19)

```css
:root {
  /* Colores existentes... */
  --accent-color: #10b981;     /* Nuevo color de acento */
  --dark-color: #1f2937;       /* Color oscuro personalizado */
}
```

### 2. Crear Nuevos Gradientes
**Archivo:** `admin-enhancement.css` (después de línea 20)

```css
--custom-gradient: linear-gradient(135deg, #tu-color-1 0%, #tu-color-2 100%);
```

### 3. Personalizar Animaciones
**Archivo:** `base.html` (después de línea 280)

```css
@keyframes tuAnimacion {
  from { /* estado inicial */ }
  to { /* estado final */ }
}

.tu-clase {
  animation: tuAnimacion 0.5s ease-out;
}
```

## 📱 Personalización Responsive

### 1. Breakpoints Móvil
**Archivo:** `base.html` (línea 260)

```css
@media (max-width: 768px) {  /* Cambiar 768px por 992px para tablets */
  /* Estilos móviles */
}
```

### 2. Ocultar Elementos en Móvil
```css
@media (max-width: 768px) {
  .elemento-a-ocultar {
    display: none !important;
  }
}
```

## 🎨 Ejemplos de Temas Predefinidos

### Tema Oscuro
```css
:root {
  --primary-color: #4c1d95;
  --secondary-color: #1e1b4b;
  --bg-light: #111827;
  --text-muted: #9ca3af;
}
```

### Tema Verde Natura
```css
:root {
  --primary-color: #059669;
  --secondary-color: #047857;
  --bg-light: #f0fdf4;
}
```

### Tema Rosa Moderno
```css
:root {
  --primary-color: #ec4899;
  --secondary-color: #be185d;
  --bg-light: #fdf2f8;
}
```

## 🛠️ Consejos de Desarrollo

1. **Usa las variables CSS** para mantener consistencia
2. **Prueba en móvil** después de cada cambio
3. **Guarda copias de seguridad** antes de cambios grandes
4. **Usa comentarios** para documentar tus modificaciones
5. **Mantén la accesibilidad** con suficiente contraste

## 📞 Estructura de Clases Útiles

- `.metric-card` - Tarjetas de métricas en dashboard
- `.quick-action-card` - Botones de acceso rápido
- `.user-avatar` - Avatar de usuario
- `.search-container` - Contenedor de búsqueda
- `.status-indicator` - Indicadores de estado

---

**💡 Tip:** Usa las herramientas de desarrollador del navegador (F12) para probar cambios en vivo antes de editarlos en el código.
