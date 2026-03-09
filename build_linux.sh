#!/bin/bash

# Configuración
APP_NAME="BeatBoard"
VERSION="1.0.27"
IMAGE_NAME="beatboard-builder"
OUTPUT_DIR="./release"
APPDIR_NAME="BeatBoard_appdir"

echo "🚀 Iniciando automatización de compilación para $APP_NAME v$VERSION..."

# 1. Limpieza inicial
echo "🧹 Limpiando compilaciones anteriores..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# 2. Construcción de la imagen Podman
echo "📦 Construyendo imagen de Ubuntu 22.04 (Python 3.10)..."
podman build -t $IMAGE_NAME -f Dockerfile.ubuntu22 .

if [ $? -ne 0 ]; then
    echo "❌ Error en la construcción de la imagen."
    exit 1
fi

# 3. Extracción de binarios
echo "📤 Extrayendo binarios del contenedor..."
podman run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/mnt:Z" \
  $IMAGE_NAME \
  cp -rv /build/output/. /mnt/

# 4. Preparación para AppImage
echo "🏗️  Preparando estructura de AppImage..."
# Aseguramos que AppRun y el .desktop estén en su sitio
# (Asumiendo que los creaste dentro de tu carpeta de proyecto o los generamos aquí)

cat <<EOF > "$OUTPUT_DIR/$APPDIR_NAME/BeatBoard.desktop"
[Desktop Entry]
Type=Application
Name=BeatBoard
Comment=Escritura creativa y gestión de guiones
Exec=BeatBoard_launch
Icon=app_icon
Terminal=false
Categories=Office;TextEditor;Qt;
Keywords=writing;creative;script;
EOF

cat <<'EOF' > "$OUTPUT_DIR/$APPDIR_NAME/AppRun"
#!/bin/sh
# Obtenemos la ruta donde está montada la AppImage
HERE=$(dirname "$(readlink -f "$0")")

# Ejecutamos el binario (sin la barra extra que daba error)
exec "$HERE/BeatBoard_launch" "$@"
EOF

chmod +x "$OUTPUT_DIR/$APPDIR_NAME/AppRun"
cp beatboard/ui/icons/app_icon.png "$OUTPUT_DIR/$APPDIR_NAME/"

# 5. Creación de la AppImage
if [ -f "./tools/appimagetool-x86_64.AppImage" ]; then
    echo "💎 Generando AppImage..."
    ./tools/appimagetool-x86_64.AppImage \
        "$OUTPUT_DIR/$APPDIR_NAME" \
        "$OUTPUT_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"
else
    echo "⚠️  No se encontró appimagetool-x86_64.AppImage en la raíz. Saltando paso de AppImage."
fi

# 6. Limpieza de imagenes Podman:

read -p "¿Quieres eliminar las imágenes Podman de compilación? (y/N): " respuesta

# Convertir a minúsculas y verificar
if [[ "$respuesta" =~ ^[yY](es)?$ ]]; then
    echo "Iniciando limpieza..."
    podman image prune -f
    echo "🧹 ¡Listo! Imágenes eliminadas."
else
    echo "Operación cancelada."
fi

echo "✅ Proceso finalizado. Archivos disponibles en: $OUTPUT_DIR"
