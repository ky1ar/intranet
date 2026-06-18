# Wiki FDM: Guía rápida de Cura

Aprende el flujo básico para preparar un modelo 3D en Cura y generar el archivo listo para imprimir en una impresora FDM.

---

## 1. ¿Qué es Cura?

Cura es un programa laminador o *slicer*. Su función es convertir un modelo 3D, como un archivo STL, OBJ o 3MF, en un archivo que la impresora pueda leer.

En Cura podrás configurar parámetros como altura de capa, relleno, temperatura, velocidad, soportes y adherencia a la cama.

**[SCREENSHOT 01: Pantalla principal de Cura]**

---

## 2. Conoce la interfaz principal

La pantalla principal de Cura se divide en varias zonas importantes:

- **Área de trabajo:** donde se visualiza el modelo sobre la cama de impresión.
- **Selector de impresora:** permite elegir el equipo configurado.
- **Panel de parámetros:** donde se ajusta la calidad, material, relleno, soportes y más.
- **Herramientas de modelo:** mover, escalar, rotar y duplicar.
- **Botón de laminar:** genera el archivo de impresión.

**[SCREENSHOT 02: Interfaz de Cura con zonas señaladas]**

**Tip K3D:** Antes de laminar, verifica que la impresora, el material y la boquilla seleccionada sean correctos.

---

## 3. Agregar o seleccionar tu impresora

Antes de preparar un modelo, debes asegurarte de tener seleccionada la impresora correcta.

Pasos:

1. Ingresa al selector de impresora.
2. Elige el modelo de impresora configurado.
3. Verifica el volumen de impresión.
4. Confirma el tamaño de boquilla, usualmente 0.4 mm.

**[SCREENSHOT 03: Selector de impresora en Cura]**

**Recomendación:** Si tu modelo de impresora no aparece, puedes usar un perfil compatible o solicitar soporte a Krear 3D.

---

## 4. Importar un archivo STL, OBJ o 3MF

Para cargar un modelo:

1. Haz clic en el botón de abrir archivo.
2. Selecciona el archivo STL, OBJ o 3MF.
3. Espera a que el modelo aparezca sobre la cama.
4. Verifica que esté bien posicionado.

**[SCREENSHOT 04: Botón para importar archivo]**

**[SCREENSHOT 05: Modelo cargado sobre la cama]**

**Tip K3D:** Si el modelo aparece muy pequeño o muy grande, revisa la escala antes de laminar.

---

## 5. Herramientas básicas del modelo

Cura permite modificar la posición, tamaño y orientación del modelo antes de imprimir.

### Mover

Sirve para cambiar la posición del modelo sobre la cama.

**[SCREENSHOT 06: Herramienta Mover]**

### Escalar

Permite aumentar o reducir el tamaño del modelo.

**[SCREENSHOT 07: Herramienta Escalar]**

### Rotar

Permite girar el modelo para mejorar la orientación de impresión.

**[SCREENSHOT 08: Herramienta Rotar]**

### Espejo

Permite invertir el modelo en un eje.

**[SCREENSHOT 09: Herramienta Espejo]**

**Recomendación:** Una buena orientación puede reducir soportes, mejorar la resistencia y acortar el tiempo de impresión.

---

## 6. Parámetros básicos de impresión

Los parámetros definen cómo se imprimirá el modelo.

### Altura de capa

Determina el nivel de detalle de la impresión.

- **0.12 mm:** más detalle, más tiempo.
- **0.20 mm:** equilibrio recomendado.
- **0.28 mm:** impresión más rápida, menos detalle.

**[SCREENSHOT 10: Parámetro Altura de capa]**

**Tip K3D:** Para empezar, usa 0.20 mm en PLA.

### Paredes

Define el grosor exterior de la pieza.

- 2 paredes: uso básico.
- 3 paredes: mayor resistencia.
- 4 paredes o más: piezas funcionales o resistentes.

**[SCREENSHOT 11: Parámetro Paredes]**

### Relleno

Define cuánto material se usará dentro del modelo.

- 10%: piezas decorativas.
- 15% a 20%: uso general.
- 30% o más: piezas resistentes.

**[SCREENSHOT 12: Parámetro Relleno / Infill]**

### Temperatura

La temperatura depende del material utilizado.

| Material | Boquilla aprox. | Cama aprox. |
|---|---:|---:|
| PLA | 190–220 °C | 50–60 °C |
| PETG | 220–250 °C | 70–85 °C |
| ABS | 235–260 °C | 90–110 °C |
| TPU | 210–240 °C | 40–60 °C |

**[SCREENSHOT 13: Parámetro Material / Temperatura]**

**Tip K3D:** Revisa siempre la temperatura recomendada en la etiqueta del filamento.

### Velocidad

Controla qué tan rápido imprime la máquina.

- 40–60 mm/s: recomendado para principiantes.
- 80 mm/s o más: requiere buena calibración.
- TPU: usar velocidades más bajas.

**[SCREENSHOT 14: Parámetro Velocidad]**

---

## 7. Soportes

Los soportes ayudan a imprimir zonas en el aire o voladizos.

Actívalos cuando el modelo tenga partes inclinadas o suspendidas.

Tipos comunes:

- **Soporte normal:** más estable.
- **Soporte tipo árbol:** más fácil de retirar en muchos modelos.

**[SCREENSHOT 15: Parámetro Soportes]**

**Recomendación:** No todos los modelos necesitan soporte. Revisa la vista previa antes de imprimir.

---

## 8. Adhesión a la cama

La adhesión ayuda a que la pieza se mantenga pegada durante la impresión.

Opciones comunes:

- **Skirt:** línea alrededor del modelo para purgar filamento.
- **Brim:** borde pegado a la pieza para mejorar adherencia.
- **Raft:** base completa debajo de la pieza.

**[SCREENSHOT 16: Parámetro Adhesión a la cama]**

**Tip K3D:** Si la pieza se despega, prueba usando Brim.

---

## 9. Laminar el modelo

Una vez configurados los parámetros, haz clic en **Laminar** o **Slice**.

Cura calculará:

- tiempo estimado de impresión;
- cantidad de material;
- recorrido de la boquilla;
- soportes generados;
- capas del modelo.

**[SCREENSHOT 17: Botón Laminar / Slice]**

---

## 10. Revisar la vista previa

La vista previa permite revisar el modelo capa por capa antes de imprimir.

Verifica:

- que la primera capa esté completa;
- que los soportes aparezcan donde corresponde;
- que no existan partes flotando;
- que el tiempo y material sean razonables;
- que el modelo esté bien orientado.

**[SCREENSHOT 18: Vista Preview de Cura]**

**Recomendación:** Nunca envíes a imprimir sin revisar la vista previa.

---

## 11. Guardar el archivo para imprimir

Después de laminar, puedes guardar el archivo en formato G-code.

Pasos:

1. Haz clic en guardar archivo.
2. Selecciona la memoria SD, USB o carpeta.
3. Lleva el archivo a la impresora.
4. Inicia la impresión desde la pantalla del equipo.

**[SCREENSHOT 19: Guardar G-code]**

**Nota:** Algunas impresoras permiten enviar el archivo por red, WiFi o nube, según el modelo.

---

## 12. Checklist antes de imprimir

Antes de iniciar una impresión, revisa:

- La cama está limpia.
- El filamento está cargado correctamente.
- La boquilla no está obstruida.
- La impresora está nivelada o calibrada.
- El archivo corresponde al modelo correcto.
- El material seleccionado coincide con el filamento.
- La primera capa se adhiere correctamente.

**[SCREENSHOT 20: Checklist visual antes de imprimir]**

---

## 13. Perfil inicial recomendado para PLA

Para usuarios nuevos, puedes empezar con estos valores:

| Parámetro | Valor sugerido |
|---|---:|
| Altura de capa | 0.20 mm |
| Boquilla | 0.4 mm |
| Temperatura de boquilla | 200–210 °C |
| Temperatura de cama | 55–60 °C |
| Relleno | 15%–20% |
| Velocidad | 50 mm/s |
| Soportes | Solo si el modelo lo requiere |
| Adhesión | Skirt o Brim |

**[SCREENSHOT 21: Perfil básico PLA en Cura]**

---

## 14. Errores comunes rápidos

### La pieza no se pega a la cama

Posibles causas: cama sucia, mala nivelación, temperatura baja, primera capa muy alta o falta de adhesión.

Solución recomendada: limpia la cama, calibra la plataforma, usa Brim y revisa el Z-offset.

### La impresión tiene hilos

Posibles causas: temperatura muy alta, retracción insuficiente o filamento húmedo.

Solución recomendada: baja la temperatura, revisa retracción y seca el filamento si es necesario.

### Las capas se separan

Posibles causas: temperatura baja, ventilación incorrecta o material mal configurado.

Solución recomendada: sube la temperatura, revisa la velocidad y usa el perfil correcto.

### Los soportes son difíciles de retirar

Posibles causas: densidad de soporte alta, distancia entre soporte y pieza muy baja u orientación poco favorable.

Solución recomendada: reduce densidad, prueba soporte tipo árbol o cambia la orientación del modelo.

---

## Soporte Krear 3D

Si necesitas ayuda, envíanos fotos o videos del problema para poder orientarte mejor.

**Soporte técnico vía WhatsApp:** +51 970 539 751  
**Atención únicamente por chat.**
