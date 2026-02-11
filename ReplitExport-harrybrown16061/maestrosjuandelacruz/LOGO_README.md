# Configuración del Logo

## Instalación del Logo

Para agregar el logo de la Residencia Escolar MJC:

### Opción 1: Usar archivo PNG (Recomendado)
1. Guarda la imagen del logo como `logo.png` en la carpeta raíz del proyecto (misma carpeta que `index.html`)
2. El sitio cargará automáticamente la imagen

### Opción 2: Logo SVG Fallback
Si no tienes el archivo `logo.png`, el sitio mostrará un logo SVG alternativo automáticamente. Este es menos visualmente atractivo pero funcional.

## Características

✅ **Header mejorado** con:
- Fondo degradado azul oscuro a índigo
- Logo redondo con sombra
- Nombre e información de la residencia
- Navegación con efectos hover

✅ **Barra de navegación**:
- Colores coordinados con el header
- Enlaces con subrayado animado al pasar el mouse
- Navegación mobile con opciones de emojis

✅ **Carga automática**:
- Intenta cargar `logo.png`
- Si falla, muestra logo SVG fallback
- Manejo robusto de errores

## Archivos modificados

- `index.html`: Header actualizado, logo dinámico, navegación mejorada
- `styles.css`: Estilos para header gradiente y navegación
- `LOGO_README.md`: Este archivo (instrucciones)

## Personalización

Para cambiar colores del header, edita `styles.css`:

```css
--header-bg: linear-gradient(to right, #1e3a8a, #1e40af, #4f46e5);
```

Los colores actuales son:
- Azul oscuro: `#1e3a8a`
- Azul medio: `#1e40af`
- Índigo: `#4f46e5`
