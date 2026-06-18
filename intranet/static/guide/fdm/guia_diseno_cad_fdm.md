# Guía wiki FDM: Diseño CAD para impresión 3D

**Objetivo:** explicar cómo diseñar piezas más fáciles de imprimir en FDM, reduciendo fallas, soportes innecesarios y problemas de ensamblaje.

**Nivel:** básico a intermedio  
**Tiempo estimado:** 15 a 20 min  
**Formato recomendado en web:** guía por secciones + ejemplos visuales.

---

## 1. ¿Qué es CAD y por qué importa en impresión 3D?

El CAD o diseño asistido por computadora permite crear modelos digitales que luego pueden fabricarse mediante impresión 3D. Para imprimir en FDM, el modelo debe ser sólido, cerrado y tener dimensiones compatibles con la máquina.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p04.png`

---

## 2. Tipos de modelado 3D

### Modelado sólido

Ideal para piezas funcionales, repuestos, soportes, carcasas, adaptadores y mecanismos. Trabaja con operaciones como extruir, cortar, perforar, unir y sustraer sólidos.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p05.png`

### Modelado de superficies

Útil para piezas estéticas, carcasas con curvas, formas orgánicas o diseños libres. Puede ser menos preciso si luego se requiere ensamblaje exacto.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p06.png`

### Escultura digital

Recomendada para personajes, figuras, miniaturas, joyería, texturas y detalles orgánicos.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p07.png`

---

## 3. Software recomendado según el nivel

| Necesidad | Software sugerido | Nivel |
|---|---|---|
| Aprender desde cero | Tinkercad | Básico |
| Piezas funcionales | Fusion 360, Onshape, FreeCAD | Intermedio |
| Modelado profesional | SolidWorks, Inventor, Rhino | Intermedio/avanzado |
| Escultura y personajes | Blender, ZBrush | Intermedio/avanzado |

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p08.png`

**Tip K3D:** para clientes nuevos que quieren diseñar piezas simples, Tinkercad es una buena entrada; para piezas funcionales, Fusion 360 u Onshape suelen ser mejores opciones.

---

## 4. Diseña piezas sólidas y cerradas

Para FDM, el modelo debe ser imprimible como un volumen sólido. Evita superficies abiertas, caras invertidas o paredes sin espesor.

**Reglas básicas:**
- el modelo debe estar cerrado;
- no debe tener agujeros en la malla;
- cada pared debe tener espesor real;
- evita geometría interna innecesaria;
- exporta en STL, 3MF u OBJ según el flujo usado.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p03.png`

---

## 5. Espesor mínimo de pared

Una pared muy delgada puede no imprimirse o quedar frágil. Como referencia práctica:

| Tipo de pieza | Espesor mínimo recomendado |
|---|---:|
| Decorativa | 0.8 mm a 1.2 mm |
| Uso general | 1.2 mm a 1.6 mm |
| Funcional/resistente | 1.6 mm a 2.4 mm o más |

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p04.png`

**Recomendación:** diseña paredes en múltiplos del ancho de línea. Para boquilla de 0.4 mm, valores como 0.8 mm, 1.2 mm o 1.6 mm suelen funcionar bien.

---

## 6. Usa redondeos y chaflanes

Los bordes completamente rectos pueden concentrar esfuerzos. Los redondeos o chaflanes ayudan a distribuir cargas y mejorar la resistencia.

**Úsalo en:**
- esquinas de piezas funcionales;
- soportes;
- piezas que recibirán peso;
- bases que puedan despegarse;
- zonas donde hay cambios bruscos de sección.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p05.png`

---

## 7. Orientación de impresión

La orientación influye en resistencia, acabado, uso de soporte y tiempo de impresión.

**Evalúa antes de laminar:**
- qué cara debe tener mejor acabado;
- qué dirección recibirá carga;
- si se pueden reducir soportes;
- si la base tiene suficiente contacto con la cama;
- si conviene dividir la pieza en partes.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p15.png`

**Tip K3D:** una misma pieza puede fallar o salir bien solo cambiando su orientación.

---

## 8. Diseña para reducir soportes

Los soportes aumentan tiempo, consumo de material y postprocesado. Siempre que sea posible, diseña con ángulos imprimibles.

**Buenas prácticas:**
- evita voladizos muy largos;
- usa chaflanes de 45° en lugar de salientes horizontales;
- divide piezas complejas;
- orienta el modelo para que las zonas críticas no queden suspendidas;
- usa puentes cortos cuando sea viable.

**[IMAGEN SUGERIDA]** `imagenes/tips/tips_p14.png`

---

## 9. Tolerancias para piezas que encajan

FDM no es perfectamente exacto; deja holgura en ensambles, tapas, ejes, pines o piezas que deben encajar.

| Tipo de encaje | Holgura inicial sugerida |
|---|---:|
| Encaje ajustado | 0.15 mm a 0.25 mm por lado |
| Encaje normal | 0.25 mm a 0.40 mm por lado |
| Encaje libre | 0.40 mm a 0.60 mm por lado |

**Recomendación:** imprime una pequeña prueba de tolerancia antes de fabricar una pieza final grande.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p18.png`

---

## 10. Agujeros, ejes y tornillos

Los agujeros impresos en FDM pueden salir ligeramente más pequeños por expansión del material.

**Buenas prácticas:**
- sobredimensiona agujeros pequeños;
- usa insertos térmicos si la pieza será desmontable;
- diseña paredes suficientes alrededor del agujero;
- evita roscas muy pequeñas impresas directamente;
- considera perforar o repasar el agujero después de imprimir.

**[IMAGEN SUGERIDA]** `imagenes/cad/cad_p19.png`

---

## 11. Exportación correcta del archivo

Antes de exportar:

- verifica que el modelo esté en milímetros;
- revisa que esté cerrado;
- elimina cuerpos ocultos innecesarios;
- usa STL para piezas simples;
- usa 3MF cuando quieras conservar más información del proyecto.

**CTA sugerido:** `Continuar con Bambu Studio` o `Continuar con Cura`.

---

## 12. Checklist de diseño FDM

Antes de imprimir, revisa:

- paredes con espesor suficiente;
- modelo cerrado y sin errores;
- orientación pensada para FDM;
- soportes reducidos cuando sea posible;
- tolerancias para ensambles;
- agujeros y encajes con holgura;
- redondeos en zonas de esfuerzo;
- archivo exportado correctamente.
