# HuertAlerta 🌿

**HuertAlerta** es un asistente personal diseñado para organizar y optimizar la siembra en mi huerta hogareña en Buenos Aires (Zona Norte).

El objetivo principal es recibir una notificación automática todos los viernes que me indique exactamente qué semillas de mi stock actual están en temporada óptima de siembra, asegurando que no se pase ninguna fecha importante del calendario hortícola.

## 🚀 Cómo funciona

El sistema procesa mi inventario personal de semillas y, basándose en el clima y las temporadas del Hemisferio Sur (específicamente Buenos Aires), filtra las variedades recomendadas.

- **Notificaciones semanales:** Todos los viernes recibo un reporte detallado en mi canal de Telegram.
- **Gestión de Stock:** El sistema solo recomienda variedades de las que poseo semillas actualmente.
- **Información Técnica:** Cada alerta incluye la familia de la planta, días estimados para la cosecha, tipo de desplante necesario y observaciones específicas para el cultivo.

## 📂 Estructura del Proyecto

- `seeds.json`: Mi base de datos personal con más de 50 variedades de hortalizas, aromáticas, medicinales y flores. Incluye fotos reales y datos técnicos de siembra.
- `notifier.py`: El motor que realiza el filtrado por mes y stock para generar los mensajes.
- `.github/workflows/`: La automatización que activa el aviso cada semana de forma puntual.

## 🛠️ Personalización

Para actualizar mi inventario, simplemente ajusto los valores de `stock` en el archivo de datos. El sistema está calibrado para las condiciones de suelo y temperatura de mi zona, facilitando una transición exitosa de la semilla a la planta.
