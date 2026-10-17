# Documentación del Proyecto: HuertAlerta 🌱

## 1. Resumen del Proyecto

**HuertAlerta** es un asistente personal automatizado para la gestión de una huerta hogareña en Buenos Aires (Zona Norte). El sistema se encarga de enviar notificaciones semanales a través de Telegram indicando qué semillas del inventario personal están en temporada óptima de siembra, basándose en la disponibilidad de stock y el mes actual.

## 2. Arquitectura y Flujo de Trabajo

La arquitectura de la aplicación es sencilla pero efectiva, basándose en un script de Python ejecutado de forma programada mediante GitHub Actions:

1. **GitHub Actions (Cron Job)**: Se ejecuta todos los viernes a las 12:00 UTC (9:00 AM Argentina).
2. **Ejecución del Script (`notifier.py`)**: Lee la base de datos de semillas (`seeds.json`).
3. **Lógica de Filtrado**: Filtra las semillas basándose en el mes actual y en si hay stock mayor a 0.
4. **Notificación (Telegram Bot API)**: Envía mensajes y fotos de cada semilla al chat configurado.

## 3. Estructura de Archivos

- [`.cursorrules`](file:///home/dilelu/repos/HuertAlerta/.cursorrules): Contiene las reglas para asistentes de inteligencia artificial (skill de Evidence Over Claims).
- [`.github/workflows/notify.yml`](file:///home/dilelu/repos/HuertAlerta/.github/workflows/notify.yml): Workflow de GitHub Actions que automatiza la ejecución del script cada semana.
- [`README.md`](file:///home/dilelu/repos/HuertAlerta/README.md): Información general del proyecto.
- [`notifier.py`](file:///home/dilelu/repos/HuertAlerta/notifier.py): Script principal en Python que procesa los datos y envía las notificaciones.
- [`requirements.txt`](file:///home/dilelu/repos/HuertAlerta/requirements.txt): Dependencias de Python (`requests`, `python-dotenv`).
- [`seeds.json`](file:///home/dilelu/repos/HuertAlerta/seeds.json): Base de datos en formato JSON que contiene el inventario de semillas y sus metadatos.
- `images/`: Directorio (referenciado en `seeds.json`) que almacena las fotos de las diferentes semillas/plantas.

## 4. Base de Datos de Semillas (`seeds.json`)

El inventario se almacena en un archivo JSON que contiene una lista de objetos. Cada objeto representa una variedad de semilla con los siguientes campos clave:

- `name`: Nombre de la semilla (ej. "Rúcula", "Espinaca").
- `family`: Familia botánica (ej. "Brassicaceae").
- `harvest_days`: Cantidad estimada de días hasta la cosecha.
- `removal_type`: Tipo de desplante o recolección (ej. "Continuo", "Desplante por cosecha").
- `planting_months`: Array de números (1 al 12) indicando en qué meses del año se puede sembrar.
- `stock`: Cantidad de unidades disponibles.
- `observations`: Notas adicionales sobre el cuidado o la siembra.
- `image_path`: Ruta local de la imagen correspondiente.

> [!NOTE]
> Actualmente, la base de datos cuenta con una gran variedad de especies, incluyendo hortalizas, flores, frutos y plantas medicinales.

## 5. Script de Notificación (`notifier.py`)

El script principal se encarga de todo el procesamiento de datos y la comunicación con Telegram.

### Lógica Principal:
1. Obtiene el mes actual utilizando `datetime`.
2. Lee y carga el archivo `seeds.json`.
3. Filtra la lista reteniendo únicamente aquellas semillas donde `stock > 0` y el mes actual se encuentra dentro del array `planting_months`.
4. Si no hay semillas disponibles, envía un mensaje informándolo.
5. Si hay semillas, envía un mensaje de cabecera con un resumen en forma de lista.
6. Itera sobre cada semilla filtrada y envía un mensaje detallado (y foto si existe) con su familia botánica, días de cosecha, stock, tipo de desplante y observaciones. 
   - *Detalle estético*: El script oculta inteligentemente el nombre de la familia si ya está contenido en el nombre de la planta.

### Conexión con Telegram:
El script utiliza dos variables de entorno principales:
- `TELEGRAM_BOT_TOKEN`: El token del bot de Telegram.
- `TELEGRAM_CHAT_ID`: El ID del chat o usuario que recibirá los mensajes.

Utiliza la librería `requests` para realizar peticiones POST a la API de Telegram (`sendPhoto` y `sendMessage`).

## 6. Automatización (GitHub Actions)

El workflow `notify.yml` está configurado para ejecutarse:
- De forma programada (`cron: '0 12 * * 5'`) todos los viernes.
- De forma manual (`workflow_dispatch`).

### Pasos del Workflow:
1. **Checkout y Setup**: Descarga el código y configura Python 3.10.
2. **Dependencias**: Instala las librerías indicadas en `requirements.txt`.
3. **Ejecución**: Ejecuta `python notifier.py` pasando los secretos de GitHub como variables de entorno.
4. **Keepalive Commit**: Ejecuta un script en bash que revisa hace cuántos días fue el último commit. Si pasaron más de 50 días, realiza un commit vacío automáticamente. Esto previene que GitHub desactive los cron jobs por inactividad del repositorio (GitHub pausa cron jobs tras 60 días sin actividad).

## 7. Próximos Pasos y Mantenimiento

- Para agregar nuevas semillas: Añadir un nuevo objeto JSON a `seeds.json`.
- Para actualizar inventario: Modificar el valor de `stock` en el objeto correspondiente.
- Las imágenes asociadas deben subirse a la carpeta `images/` para que Telegram pueda enviarlas junto con la descripción.

> [!TIP]
> Dado que el script actualmente envía la notificación secuencialmente mediante peticiones a la API de Telegram, si la lista de semillas es muy grande, la ejecución podría tardar un poco y estar sujeta a "Rate Limits" de Telegram.
