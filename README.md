# HuertAlerta 🌿

**HuertAlerta** es un asistente personal diseñado para organizar y optimizar la siembra en mi huerta hogareña en Buenos Aires (Zona Norte).

El objetivo principal es recibir una notificación automática todos los viernes que me indique exactamente qué semillas de mi stock actual están en temporada óptima de siembra, asegurando que no se pase ninguna fecha importante del calendario hortícola.

---

## 🚀 Cómo funciona

El sistema procesa mi inventario personal de semillas y, basándose en el clima y las temporadas del Hemisferio Sur (específicamente Buenos Aires), filtra las variedades recomendadas.

* **Notificación semanal compacta:** Todos los viernes recibo un reporte limpio y unificado en mi canal de Telegram con todas las variedades que se pueden sembrar este mes.
* **Fichas interactivas en GitHub Pages:** Cada planta de la lista contiene un enlace directo a su ficha técnica visual alojada en [GitHub Pages](https://dilelu94.github.io/HuertAlerta/). Al tocarla, se abre la ficha con fotos reales de la planta, familia botánica, días estimados a la cosecha, stock actual, método de desplante/siembra y consejos prácticos de cultivo.
* **Fichas Markdown individuales:** Cada variedad cuenta con su propia ficha individual en la carpeta [`plantas/`](plantas/) para fácil consulta y edición desde GitHub.
* **Gestión de Stock:** El sistema solo recomienda variedades de las que poseo semillas actualmente (`stock > 0`).
* **Protección Keepalive:** Cuenta con un script automático que evita que GitHub Actions desactive los cron jobs semanales por inactividad del repositorio.

---

## 📂 Estructura del Proyecto

* `seeds.json`: Base de datos estructurada con más de 65 variedades de hortalizas, aromáticas, medicinales, frutos y flores. Cada variedad cuenta con su ID, fotos, requerimientos y datos técnicos de siembra.
* `notifier.py`: Motor en Python ejecutado por GitHub Actions que filtra las semillas del mes y genera el mensaje enriquecido para Telegram.
* `index.html`: Web interactiva alojada en GitHub Pages que presenta las tarjetas visuales de cada planta con enlaces directos (`#pID`).
* `plantas/`: Directorio con archivos Markdown (`.md`) individuales por planta.
* `images/`: Galería de fotos reales de cultivos y hojas de referencia.
* `.github/workflows/notify.yml`: Flujo de trabajo programado que activa el aviso cada viernes a las 9:00 AM (Argentina).

---

## 🛠️ Personalización y Mantenimiento

Para actualizar el inventario, simplemente se modifican los valores de `stock` en `seeds.json`. El sistema está calibrado para las condiciones climáticas y de suelo de Buenos Aires, garantizando una transición exitosa de la semilla a la cosecha.
