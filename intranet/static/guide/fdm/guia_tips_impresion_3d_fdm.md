# Guía wiki FDM: Tips para mejorar tus impresiones 3D

**Objetivo:** dar recomendaciones rápidas para mejorar calidad, adherencia, resistencia y acabado en impresiones FDM.

**Nivel:** básico  
**Tiempo estimado:** 8 a 12 min  
**Formato recomendado en web:** tarjetas con tips + imágenes ejemplo.

---

## 1. Empieza con un perfil estándar

Si es tu primera impresión, evita modificar demasiados parámetros. Usa un perfil estándar del software y cambia solo lo necesario.

**Recomendación inicial:**
- PLA como material;
- altura de capa 0.20 mm;
- relleno 15% a 20%;
- soportes solo si el modelo lo requiere;
- velocidad estándar del equipo.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p02.png`

---

## 2. La primera capa es lo más importante

Una mala primera capa puede arruinar toda la impresión.

**Debe verse:**
- continua;
- ligeramente aplastada;
- bien adherida;
- sin espacios entre líneas;
- sin filamento raspado por la boquilla.

**Acciones útiles:**
- limpia la cama;
- calibra o ajusta Z-offset;
- reduce velocidad de primera capa;
- usa Brim si la pieza tiene poca base.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p04.png`

---

## 3. Orienta la pieza antes de laminar

La orientación define cuánto soporte necesitarás, qué acabado tendrá la pieza y qué tan resistente será.

**Evalúa:**
- la cara visible;
- la dirección de esfuerzo;
- el contacto con la cama;
- el uso de soportes;
- el tiempo de impresión.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p15.png`

---

## 4. Usa soportes solo cuando sean necesarios

Los soportes ayudan, pero también pueden dejar marcas y aumentar el tiempo.

**Recomendación:**
- si el voladizo supera aprox. 45°, probablemente necesite soporte;
- prueba soporte tipo árbol para figuras o geometrías orgánicas;
- usa soporte solo desde la placa cuando quieras reducir marcas;
- cambia la orientación antes de activar soportes excesivos.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p14.png`

---

## 5. Ajusta la temperatura según el material

Cada filamento tiene un rango de temperatura. Imprimir muy frío puede causar subextrusión; imprimir muy caliente puede generar hilos o mala definición.

| Material | Boquilla aprox. | Cama aprox. |
|---|---:|---:|
| PLA | 190-220 °C | 50-60 °C |
| PETG | 220-250 °C | 70-85 °C |
| ABS | 235-260 °C | 90-110 °C |
| TPU | 210-240 °C | 40-60 °C |
| ASA | 240-260 °C | 90-110 °C |

**Tip K3D:** usa la etiqueta del filamento como referencia principal.

**[IMAGEN SUGERIDA]** captura del panel de filamento en Bambu Studio o Cura.

---

## 6. Controla el relleno y las paredes

No siempre necesitas mucho relleno. Muchas veces aumentar paredes mejora más la resistencia que subir demasiado el infill.

**Referencia rápida:**
- piezas decorativas: 10% a 15% de relleno;
- piezas generales: 15% a 20%;
- piezas funcionales: 25% a 40%;
- piezas resistentes: más paredes + material adecuado.

**[IMAGEN SUGERIDA]** captura del panel de relleno/Strength en Bambu Studio.

---

## 7. Mantén el filamento seco

La humedad puede causar burbujas, mala superficie, hilos y capas débiles.

**Señales de humedad:**
- sonido de burbujeo en la boquilla;
- textura rugosa;
- stringing excesivo;
- baja resistencia de la pieza.

**Soluciones:**
- guarda filamentos en bolsa sellada;
- usa desecante;
- seca materiales como PETG, TPU, Nylon o PC antes de imprimir.

**[IMAGEN SUGERIDA]** foto de filamento en caja seca o secador de filamento.

---

## 8. Limpia y revisa la impresora

Pequeños problemas mecánicos pueden generar grandes fallas.

**Revisa periódicamente:**
- boquilla;
- extrusor;
- correas;
- cama;
- ruedas o guías;
- ventiladores;
- restos de filamento.

**[IMAGEN SUGERIDA]** foto de mantenimiento básico de impresora FDM.

---

## 9. No imprimas piezas grandes sin prueba previa

Antes de imprimir una pieza grande o de muchas horas, realiza una prueba pequeña.

**Puedes probar:**
- tolerancias;
- encaje;
- temperatura;
- resistencia;
- orientación;
- calidad de superficie.

**Tip K3D:** una prueba de 20 minutos puede evitar perder 8 horas de impresión.

---

## 10. Checklist final antes de imprimir

- Modelo correcto.
- Material correcto.
- Boquilla correcta.
- Perfil correcto.
- Cama limpia.
- Primera capa revisada.
- Soportes revisados en preview.
- Tiempo y material validados.
- Filamento suficiente.

**CTA sugerido:** `Ir a guía de errores comunes`.
