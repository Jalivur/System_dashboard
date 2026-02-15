# 🎨 Guía de Temas Personalizados

El Sistema de Monitoreo incluye **15 temas pre-configurados** que puedes cambiar fácilmente.

---

## 🚀 Cambiar Tema (Método Gráfico)

1. **Abre el dashboard**
```bash
python3 main.py
```

2. **Haz clic en "🎨 Cambiar Tema"** en el menú principal

3. **Selecciona tu tema favorito** de la lista

4. **Haz clic en "Aplicar y Reiniciar"**

5. **Reinicia el dashboard**
```bash
# Cierra todas las ventanas y ejecuta de nuevo
python3 main.py
```

**¡Listo!** Tu nuevo tema estará activo.

---

## 🎨 Temas Disponibles (15 Temas)

### 1. **Cyberpunk** (Original) ⚡
- **Estilo**: Futurista, neón cyan
- **Colores**: Cyan brillante + Negro
- **Perfecto para**: Look futurista original

### 2. **Matrix** 🟢
- **Estilo**: Inspirado en Matrix
- **Colores**: Verde neón + Negro puro
- **Perfecto para**: Fans de Matrix, hackers

### 3. **Sunset** 🌅
- **Estilo**: Colores cálidos de atardecer
- **Colores**: Naranja + Púrpura
- **Perfecto para**: Ambiente relajado, cálido

### 4. **Ocean** 🌊
- **Estilo**: Colores del océano
- **Colores**: Azul cielo + Azul marino
- **Perfecto para**: Look fresco y limpio

### 5. **Dracula** 🧛
- **Estilo**: Tema popular Dracula
- **Colores**: Púrpura pastel + Gris oscuro
- **Perfecto para**: Fans de Dracula theme

### 6. **Nord** ❄️
- **Estilo**: Tema nórdico, frío
- **Colores**: Azul hielo + Gris polar
- **Perfecto para**: Look minimalista, nórdico

### 7. **Tokyo Night** 🌃
- **Estilo**: Noche en Tokio
- **Colores**: Azul brillante + Negro azulado
- **Perfecto para**: Fans de anime, noche

### 8. **Monokai** 🎨
- **Estilo**: Tema clásico de editores
- **Colores**: Azul claro + Verde oscuro
- **Perfecto para**: Programadores

### 9. **Gruvbox** ☕
- **Estilo**: Retro, cálido
- **Colores**: Naranja + Marrón
- **Perfecto para**: Look vintage

### 10. **Solarized Dark** ☀️
- **Estilo**: Tema científico popular
- **Colores**: Azul + Tonos tierra
- **Perfecto para**: Fácil a la vista

### 11. **One Dark** 🌑
- **Estilo**: Tema de Atom/VSCode
- **Colores**: Azul claro + Gris oscuro
- **Perfecto para**: Desarrollo

### 12. **Synthwave** 🌆
- **Estilo**: Retro 80s, neón
- **Colores**: Rosa neón + Púrpura
- **Perfecto para**: Estética retro-futurista

### 13. **GitHub Dark** 🐙
- **Estilo**: Tema de GitHub
- **Colores**: Azul GitHub + Negro
- **Perfecto para**: Familiar y profesional

### 14. **Material** 📱
- **Estilo**: Material Design
- **Colores**: Azul material + Gris
- **Perfecto para**: Look moderno

### 15. **Ayu Dark** 🎯
- **Estilo**: Minimalista, limpio
- **Colores**: Azul cielo + Negro
- **Perfecto para**: Simplicidad

---

## ⚙️ Cambiar Tema Manualmente

Si prefieres cambiar el tema editando archivos:

### Método 1: Editar archivo de configuración

```bash
# Editar el archivo de tema
nano data/theme_config.json
```

```json
{
  "selected_theme": "matrix"
}
```

Opciones válidas:
- `cyberpunk` (original)
- `matrix`
- `sunset`
- `ocean`
- `dracula`
- `nord`
- `tokyo_night`
- `monokai`
- `gruvbox`
- `solarized_dark`
- `one_dark`
- `synthwave`
- `github_dark`
- `material`
- `ayu_dark`

### Método 2: Desde Python

```python
from config.themes import save_selected_theme

# Cambiar a tema Matrix
save_selected_theme("matrix")

# Reiniciar el dashboard
```

---

## 🎨 Crear Tu Propio Tema

### Opción 1: Editar `config/themes.py`

Añade tu tema al diccionario `THEMES`:

```python
"mi_tema": {
    "name": "Mi Tema Personalizado",
    "colors": {
        "primary": "#ff00ff",      # Color principal
        "secondary": "#330033",    # Color secundario
        "success": "#00ff00",      # Verde éxito
        "warning": "#ffaa00",      # Naranja advertencia
        "danger": "#ff0000",       # Rojo peligro
        "bg_dark": "#000000",      # Fondo oscuro
        "bg_medium": "#111111",    # Fondo medio
        "bg_light": "#222222",     # Fondo claro
        "text": "#ffffff",         # Color texto
        "border": "#ff00ff"        # Color bordes
    }
}
```

### Opción 2: Usar la función create_custom_theme

```python
from config.themes import create_custom_theme, THEMES

mi_tema = create_custom_theme(
    name="Mi Tema",
    colors={
        "primary": "#ff00ff",
        "secondary": "#330033",
        "success": "#00ff00",
        "warning": "#ffaa00",
        "danger": "#ff0000",
        "bg_dark": "#000000",
        "bg_medium": "#111111",
        "bg_light": "#222222",
        "text": "#ffffff",
        "border": "#ff00ff"
    }
)

# Añadirlo a THEMES
THEMES["mi_tema"] = mi_tema
```

---

## 🎯 Tips para Colores

### Colores Recomendados por Categoría

**Fondos oscuros:**
- Negro: `#000000`
- Negro azulado: `#0a0e14`
- Gris muy oscuro: `#1e1f29`

**Primarios (color principal del tema):**
- Cyan: `#00ffff`
- Verde neón: `#00ff00`
- Azul: `#61afef`
- Rosa: `#f92aad`

**Texto:**
- Blanco: `#ffffff`
- Gris claro: `#abb2bf`
- Beige: `#f8f0e3`

**Estados:**
- Éxito (verde): `#00ff00`, `#50fa7b`, `#a3be8c`
- Advertencia (amarillo/naranja): `#ffaa00`, `#e5c07b`
- Peligro (rojo): `#ff3333`, `#f85149`

---

## 🔍 Ver Preview de Todos los Temas

```python
from config.themes import get_theme_preview

print(get_theme_preview())
```

Esto mostrará todos los temas con sus colores principales.

---

## 📸 Capturas de Pantalla

(Los temas se ven mejor en vivo, pero aquí una guía rápida)

**Temas Neón**: Cyberpunk, Matrix, Synthwave
- Alto contraste
- Colores brillantes
- Efecto futurista

**Temas Pastel**: Dracula, Nord, Material
- Colores suaves
- Fácil a la vista
- Profesional

**Temas Cálidos**: Sunset, Gruvbox
- Naranja/marrones
- Acogedor
- Vintage

**Temas Fríos**: Ocean, Tokyo Night, Ayu
- Azules
- Moderno
- Limpio

---

## 🐛 Solución de Problemas

### El tema no cambia al reiniciar

**Verifica:**
```bash
# Ver tema guardado
cat data/theme_config.json

# Debe mostrar:
# {"selected_theme": "tu_tema"}
```

### Error al cargar tema

El sistema volverá automáticamente al tema `cyberpunk` por defecto.

### Los colores se ven mal

Algunos terminales/pantallas pueden mostrar colores ligeramente diferentes. Prueba otro tema o ajusta los colores manualmente.

---

## 💡 Recomendaciones

**Para trabajar de noche**: Nord, Tokyo Night, Ayu Dark
**Para trabajar de día**: Ocean, Material, GitHub Dark
**Para impresionar**: Synthwave, Cyberpunk, Matrix
**Para productividad**: One Dark, Solarized Dark, Dracula

---

## 🎨 Combinaciones Populares

### Gaming Setup
- **Tema**: Synthwave o Cyberpunk
- **Monitor**: RGB sincronizado

### Desarrollo
- **Tema**: One Dark o Dracula
- **Monitor**: Editor con mismo tema

### Server Monitoring
- **Tema**: Matrix o GitHub Dark
- **Monitor**: Terminal verde

---

## 📝 Guardar Tus Favoritos

Crea un archivo con tus temas preferidos:

```bash
# Crear lista de favoritos
nano data/my_favorite_themes.txt
```

```
Trabajo: one_dark
Noche: nord
Fin de semana: synthwave
```

---

## 🚀 Próximamente

- [ ] Temas claros (light themes)
- [ ] Editor de temas visual
- [ ] Importar temas desde archivo
- [ ] Compartir temas entre usuarios

---

**¡Disfruta personalizando tu dashboard!** 🎨✨
