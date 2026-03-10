# Manual de Usuario de BeatBoard

![main](../../imgs/beatboard_002.png)

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Gestión de Beats](#gestión-de-beats)
5. [Conexiones entre Beats](#conexiones-entre-beats)
6. [Herramientas del Lienzo](#herramientas-del-lienzo)
7. [Personalización](#personalización)
8. [Exportación y Guardado](#exportación-y-guardado)
9. [Atajos de Teclado](#atajos-de-teclado)
10. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

BeatBoard es una aplicación de escritorio de pizarra virtual para escritores, inspirada en el Beat Board de Final Draft. Es una herramienta especialmente diseñada para guionistas, escritores de relatos y novelas que necesitan visualizar la estructura de sus historias.

Con BeatBoard puedes:
- Crear un lienzo infinito donde organizar tus ideas
- Crear tarjetas de beat con título y contenido
- Conectar beats con líneas de flujo curvas
- Organizar y reordernar tus elementos visualmente
- Personalizar la apariencia con temas y colores
- Exportar tu trabajo a PDF o texto

---

## Primeros Pasos

### Instalación

Para ejecutar BeatBoard:

1. **Desde código fuente**:
   ```bash
   cd BeatBoard
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate  # Windows
   pip install pyside6
   python -m beatboard.app.main
   ```

2. **Ejecutable pre-compilado**:
   Descarga el archivo ejecutable desde la página de lanzamientos y ejecútalo directamente.

### Crear tu Primer Proyecto

Al iniciar BeatBoard, se crea automáticamente un proyecto en blanco. Puedes comenzar inmediatamente a crear beats en el lienzo.

Para guardar tu proyecto:
1. Ve a **Archivo > Guardar** (o presiona **Ctrl+S**)
2. Elige la ubicación y el nombre para tu archivo
3. Los proyectos de BeatBoard tienen extensión `.bbp`

---

## Interfaz de Usuario

![beatboard_interface](../../imgs/manual/0001.png)

La interfaz de BeatBoard se divide en las siguientes áreas:

### Barra de Herramientas

![beatboard_interface](../../imgs/manual/0002.png)

La barra de herramientas proporciona acceso rápido a las funciones más utilizadas:

| Botón | Función | Atajo |
|-------|---------|-------|
| Nuevo | Crear nuevo proyecto | Ctrl+N |
| Abrir | Abrir proyecto existente | Ctrl+O |
| Guardar | Guardar proyecto | Ctrl+S |
| + (Acercar) | Aumentar zoom | Ctrl++ |
| - (Alejar) | Disminuir zoom | Ctrl+- |
| Zoom | Zoom de selección de área | Z |
| Ajustar | Ajustar vista al contenido | Ctrl+0 |
| Centrar | Centrar vista en el origen | - |
| Conectar | Activar modo conexión | C |

### Panel de Propiedades

![beatboard_interface](../../imgs/manual/0003.png)

El panel de propiedades (ubicado a la derecha) permite editar el elemento seleccionado:

- **Ningún beat seleccionado**: Muestra un mensaje indicando "Nada seleccionado"
- **Un beat seleccionado**: Permite editar título, contenido, color y visibilidad del título
- **Varios beats seleccionados**: Permite editar propiedades comunes a todos ellos
- **Conexiónes seleccionada**: Permite editar color, grosor, forma de nodos y etiqueta

### Barra de Estado

La barra inferior muestra información útil:
- Cantidad de beats en el proyecto
- Nivel de zoom actual
- Estado del proyecto (Modificado/Guardado)
- Posición del cursor en el lienzo

---

## Gestión de Beats

![beatboard_interface](../../imgs/manual/0004.png)

### Crear un Beat

**Método 1 - Doble clic**:
1. Haz doble clic en cualquier área vacía del lienzo
2. Se creará un nuevo beat en esa posición

### Editar un Beat

![beatboard_interface](../../imgs/manual/0005.png)

**Edición rápida**:
1. Haz doble clic en el beat que deseas editar
2. Se abrirá el diálogo de edición de beat

![beatboard_interface](../../imgs/manual/0006.png)

**Edición desde el panel de propiedades**:
1. Selecciona el beat
2. Modifica el título o contenido directamente en el panel de propiedades
3. Los cambios se aplican automáticamente

**Editor completo**:
1. Selecciona el beat
2. En el panel de propiedades, haz clic en "Abrir editor completo"
3. Se abrirá el diálogo con opciones avanzadas de formato

### El Editor de Beat

El editor de beat ofrece las siguientes herramientas de formato:

#### Barra de Formato
- **B** (Negrita): Aplica formato en negrita al texto seleccionado
- *I* (Cursiva): Aplica formato en cursiva
- **U** (Subrayado): Aplica formato subrayado
- **Tamaño de fuente**: Selector de tamaño de letra (8-32pt)
- **H1, H2, H3**: Insertar títulos de diferentes niveles
- **•** (Viñetas): Insertar lista con viñetas
- **A** (Color de texto): Cambiar el color del texto seleccionado
- **█** (Resaltado): Aplicar color de fondo al texto
- **[Link]**: Insertar hipervínculo
- **[Code]**: Insertar texto con formato de código
- **[Quote]**: Insertar cita

#### Campos del Editor
- **Título**: Nombre del beat (opcional)
- **Contenido**: Descripción detallada del beat (soporta formato rico)
- **Color**: Selector de color del beat

### Mover un Beat

1. Haz clic sobre el beat
2. Arrastra el beat a la nueva posición
3. Suelta el botón del ratón

### Selección Múltiple

**Seleccionar varios beats**:
- Mantén presionada la tecla **Ctrl** mientras haces clic en cada beat
- O bien, arrastra un rectángulo de selección alrededor de los beats deseados

**Mover múltiples beats**:
1. Selecciona varios beats
2. Arrastra cualquiera de ellos
3. Todos los beats seleccionados se moverán juntos

### Copiar y Pegar

- **Copiar**: Selecciona el beat y presiona **Ctrl+C**
- **Cortar**: Selecciona el beat y presiona **Ctrl+X**
- **Pegar**: Presiona **Ctrl+V** para crear una copia en el centro del lienzo

### Eliminar un Beat

1. Selecciona el beat (o beats)
2. Presiona la tecla **Delete** o **Supr** o con **botón derecho > Eliminar**

### Orden Z (Profundidad)

![beatboard_interface](../../imgs/manual/0007.png)

BeatBoard permite controlar qué beats aparecen delante de otros:

| Acción | Atajo | Descripción |
|--------|-------|-------------|
| Traer al frente | Ctrl+Home | Mueve el beat a la capa más superior |
| Enviar al fondo | Ctrl+End | Mueve el beat a la capa más inferior |
| Subir uno | Ctrl+PageUp | Intercambia posición con el beat inmediatamente superior |
| Bajar uno | Ctrl+PageDown | Intercambia posición con el beat inmediatamente inferior |

### Colores de Beat

![beatboard_interface](../../imgs/manual/0008.png)

BeatBoard ofrece 10 colores predefinidos y 3 personalizables:

| Tecla | Color |
|-------|-------|
| 1 | Amarillo |
| 2 | Azul |
| 3 | Verde |
| 4 | Rojo |
| 5 | Naranja |
| 6 | Púrpura |
| 7 | Gris |
| 8 | Personalizable 1 |
| 9 | Personalizable 2 |
| 0 | Personalizable 3 |

**Cambiar color con teclado**:
1. Selecciona uno o varios beats
2. Presiona una tecla del 1 al 0

**Personalizar colores**:
1. Selecciona un beats y abre el **Editor completo**
2. Haz doble-click en uno de los tres colores personalizables y editalo

---

## Conexiones entre Beats

![beatboard_interface](../../imgs/manual/0009.png)

Las conexiones son líneas curvas que unen dos beats, mostrando el flujo de la historia.

### Crear una Conexión

**Método 1 - Barra de herramientas**:
1. Haz clic en el botón "Conectar" en la barra de herramientas (o presiona **C**)
2. El cursor cambiará a cruz
3. Haz clic en el beat de origen
4. Haz clic en el beat de destino
5. La conexión se creará automáticamente
6. Presiona **Escape** para salir del modo conexión

**Nota**: Cuando el modo conexión está activo, aparece un banner en la parte inferior del lienzo indicando "Modo 'Conexión' Activado".

### Editar una Conexión

**Seleccionar conexión**:
- Haz clic directamente sobre la línea de conexión
- La conexión se resaltará con un borde azul

![beatboard_interface](../../imgs/manual/0010.png)

**Propiedades de conexión** (en el panel de propiedades):
- **Color**: Color de la línea (rojo, azul, verde, amarillo, naranja, púrpura, gris oscuro)
- **Grosor**: Grosor de la línea (0.5 - 10 px)
- **Forma de nodos**: Forma del terminador en los extremos:
  - Círculo
  - Cuadrado
  - Flecha
  - Ninguno
- **Etiqueta**: Texto que aparece en el centro de la conexión

### Nodos Editables

![beatboard_interface](../../imgs/manual/0011.png)

Las conexiones tienen puntos de control que permiten modificar su curvatura:

1. Selecciona la conexión
2. Aparecerán dos manejadores (puntos) en la línea
3. Arrastra los manejadores para ajustar la curva
4. Doble clic en un manejador para restablecer la curvatura por defecto

### Eliminar una Conexión

1. Selecciona la conexión
2. Presiona **Delete** o **Supr**

---

## Herramientas del Lienzo

### Zoom

**Acercar**:
- Ve a **Ver > Acercar** 
- Presiona **Ctrl++**
- O usa el botón "+" en la barra de herramientas

**Alejar**:
- Ve a **Ver > Alejar**
- Presiona **Ctrl+-**
- O usa el botón "-" en la barra de herramientas

**Ajustar al contenido**:
- Ve to **Ver > Ajustar a contenido**
- Presiona **Ctrl+0**
- O usa el botón de ajustar en la barra de herramientas

**Zoom de selección de área**:
1. Presiona **Z** o haz clic en el botón de zoom en la barra de herramientas
2. Arrastra un rectángulo alrededor del área que deseas ver
3. La vista se centrará y ajustará al área seleccionada
4. Presiona **Escape** para cancelar

### Paneo (Desplazamiento)

**Con teclado**:
- Mantén presionada la tecla **Espacio**
- Arrastra el ratón para mover el lienzo

**Con ratón**:
- Mantén presionado el botón central del ratón
- Arrastra para mover el lienzo

### Cuadrícula

La cuadrícula ayuda a alinear los beats visualmente.

**Mostrar/Ocultar**:
- Ve a **Ver > Mostrar cuadrícula**
- O usa el atajo configurado

**Personalizar cuadrícula**:
1. Ve a **Ver > Opciones de cuadrícula**
2. **Tamaño de celda**: Elige entre 50, 100, 150, 200 o 250 px
3. **Color de cuadrícula**: 
   - Auto: Se adapta al tema
   - Colores predefinidos: Amarillo, Azul, Verde, Rojo, Naranja, Púrpura, Gris
   - Personalizado: Elige tu propio color

### Punto Central

![beatboard_interface](../../imgs/manual/0012.png)

El punto central (origen 0,0) se muestra como una cruz pequeña en el centro del lienzo. Haz clic en el botón "Centrar" de la barra de herramientas para mover la vista al origen.

---

## Personalización

### Temas

BeatBoard ofrece 9 temas diferentes:

**Temas claros**:
- Claro (predeterminado)
- Solarized Light
- GitHub Light
- PaperColor

**Temas oscuros**:
- Oscuro (predeterminado)
- Dracula
- Nord
- One Dark
- Material Dark

**Aplicar tema**:
1. Ve a **Preferencias > Tema**
2. Selecciona el tema deseado
3. También puedes elegir "Sistema" para usar el tema de tu sistema operativo

### Color de Fondo del Lienzo

Puedes personalizar el color de fondo del lienzo:

1. Ve a **Preferencias > Color de fondo**
2. Elige entre:
   - Blanco
   - Gris claro
   - Gris
   - Gris oscuro
   - Crema
   - Oscuro
   - Negro
   - Personalizado (elige tu propio color)

**Restablecer colores del tema**:
- Selecciona "Restablecer colores del tema" para volver a los colores predeterminados del tema actual

### Memoria de Defaults

Activa la opción **"Recordar tamaño y color del último beat"** en Preferencias para que los nuevos beats hereden el tamaño y color del último beat creado.

### Idioma

BeatBoard está disponible en 4 idiomas:
- Inglés (English)
- Español
- Francés (Français)
- Alemán (Deutsch)

Para cambiar el idioma:
1. Ve a **Preferencias > Idioma**
2. Selecciona el idioma deseado
3. Reinicia la aplicación para aplicar el cambio

### Corrección Ortográfica

BeatBoard incluye un corrector ortográfico integrado:

**Activar**:
1. Ve a **Preferencias > Corrección ortográfica > Habilitar corrección ortográfica**

**Idioma del diccionario**:
1. Ve a **Preferencias > Corrección ortográfica > Idioma del diccionario**
2. Selecciona el idioma: Inglés, Español, Francés o Alemán

**Usar el corrector**:
- Las palabras incorrectas se subrayarán en rojo
- Haz clic derecho sobre una palabra para ver sugerencias

---

## Exportación y Guardado

### Formato de Archivo

Los proyectos de BeatBoard se guardan en formato `.bbp` (JSON). Este formato incluye:
- Todos los beats (título, contenido, posición, tamaño, color)
- Todas las conexiones
- Configuración del lienzo

### Guardar Proyecto

- **Guardar**: **Ctrl+S** (guarda en el archivo actual)
- **Guardar como**: **Ctrl+Shift+S** (elige ubicación y nombre)

### Exportar a PDF

- En desarrollo

### Exportar a Texto

1. Ve a **Archivo > Exportar a texto**
2. Selecciona la ubicación y nombre del archivo
3. Se generará un archivo de texto con todos los beats

### Archivos Recientes

BeatBoard mantiene una lista de los 10 últimos archivos abiertos:

1. Ve a **Archivo > Abrir recientes**
2. Selecciona el archivo deseado

Si un archivo de la lista ya no existe, se te preguntará si deseas eliminarlo de la lista.

### Auto-guardado

BeatBoard puede guardar automáticamente tu proyecto:

1. Ve a **Preferencias > Opciones de backup**
2. Configura:
   - **Copia de seguridad al abrir**: Crea una copia al abrir el proyecto
   - **Auto-guardado**: Activa/desactiva el guardado automático
   - **Intervalo**: Cada cuánto tiempo guardar (1, 2, 5, 10, 15 o 30 minutos)
   - **Máximo de copias**: Cantidad de copias de seguridad a mantener

---

## Atajos de Teclado

### Archivo

| Atajo | Función |
|-------|---------|
| Ctrl+N | Nuevo proyecto |
| Ctrl+O | Abrir proyecto |
| Ctrl+S | Guardar proyecto |
| Ctrl+Shift+S | Guardar como |
| Ctrl+W | Cerrar proyecto |
| Ctrl+Q | Salir |

### Editar

| Atajo | Función |
|-------|---------|
| Ctrl+Z | Deshacer |
| Ctrl+Y | Rehacer |
| Ctrl+A | Seleccionar todo |
| Ctrl+C | Copiar |
| Ctrl+X | Cortar |
| Ctrl+V | Pegar |
| Delete | Eliminar selección |
| Ctrl+Home | Traer al frente |
| Ctrl+End | Enviar al fondo |
| Ctrl+PageUp | Subir uno |
| Ctrl+PageDown | Bajar uno |

### Ver

| Atajo | Función |
|-------|---------|
| Ctrl++ | Acercar |
| Ctrl+- | Alejar |
| Ctrl+0 | Ajustar a contenido |
| Espacio | Modo paneo (mantener presionado) |

### Otros Atajos

| Atajo | Función |
|-------|---------|
| 1-0 | Cambiar color de selección |
| C | Activar/desactivar modo conexión (sin selección) |
| Z | Zoom de selección (sin selección) |
| Escape | Cancelar / Deseleccionar todo |
| Doble clic (lienzo) | Crear nuevo beat |
| Doble clic (beat) | Editar beat |

---

## Solución de Problemas

### El programa no inicia

1. Verifica que tienes Python 3.10+ instalado
2. Asegúrate de haber instalado PySide6: `pip install pyside6`
3. Revisa que no haya errores en la terminal

### Los beats no se guardan

1. Verifica que tienes permisos de escritura en la carpeta
2. Asegúrate de guardar el proyecto antes de cerrar (Ctrl+S)
3. Revisa el estado del proyecto en la barra de estado (debe decir "Guardado")

### La cuadrícula no se muestra

1. Verifica que la cuadrícula esté activada: **Ver > Mostrar cuadrícula**
2. Prueba cambiando el color de cuadrícula en **Ver > Opciones de cuadrícula**

### El corrector ortográfico no funciona

1. Verifica que esté habilitado en **Preferencias > Corrección ortográfica**
2. Asegúrate de haber seleccionado el idioma correcto del diccionario

### Los colores personalizados no se guardan

1. Los colores personalizados se guardan en las preferencias, no en el proyecto
2. Se aplican automáticamente a futuros beats según la configuración

---

## Información Adicional

### Atajos del Ratón

- **Doble clic en lienzo**: Crear nuevo beat
- **Doble clic en beat**: Editar beat
- **Clic simple**: Seleccionar elemento
- **Shift + Clic**: Añadir a selección
- **Arrastrar (selección)**: Crear rectángulo de selección
- **Arrastrar (beat)**: Mover beat
- **Rueda del ratón**: Zoom (con Ctrl presionado)
- **Botón central del ratón**: Paneo

### Glosario

- **Beat**: Tarjeta individual en el lienzo que representa una escena o momento de la historia
- **Conexión**: Línea curva que une dos beats
- **Lienzo (Canvas)**: El área de trabajo donde se sitúan los beats
- **Orden Z**: Profundidad o capa de un elemento (qué aparece encima de qué)
- **Tema**: Conjunto de colores y estilos que definen la apariencia de la aplicación
- **Panel de propiedades**: Panel lateral donde se editen las propiedades del elemento seleccionado

---

## Créditos

BeatBoard fue creado por CarlyMx y está inspirado en Final Draft Beat Board.

Para más información, actualizaciones y soporte, visita el repositorio en GitHub.

---

*Manual creado para BeatBoard versión 1.0.27*
