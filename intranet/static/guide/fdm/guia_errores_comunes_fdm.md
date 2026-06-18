# Guía wiki FDM: Errores comunes de impresión 3D

**Objetivo:** ayudar al cliente a identificar rápidamente qué está fallando, cuál puede ser la causa y qué acción tomar antes de volver a imprimir.

**Nivel:** básico a intermedio  
**Tiempo estimado:** 10 a 15 min  
**Formato recomendado en web:** acordeón por problema + buscador por síntoma.

---

## 1. Cómo usar esta guía

Cuando una impresión falla, primero identifica el síntoma visual. Luego revisa las posibles causas en orden: calibración, material, parámetros de laminado y estado mecánico de la impresora.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p02.png`  
**Uso en web:** portada o banner de la guía.

---

## 2. No extruye al inicio de la impresión

**Cómo se ve:** la impresora se mueve, pero al iniciar no deposita filamento o deja líneas incompletas.

**Causas posibles:**
- la boquilla está demasiado cerca de la cama;
- el filamento no fue cargado correctamente;
- la boquilla está parcialmente obstruida;
- la primera capa está configurada muy rápida;
- el extrusor no está empujando el filamento.

**Soluciones recomendadas:**
1. Revisa la nivelación o el Z-offset.
2. Carga nuevamente el filamento y verifica que salga por la boquilla.
3. Limpia o destapa la boquilla si el flujo es irregular.
4. Reduce la velocidad de primera capa.
5. Usa una línea de purga o skirt antes de imprimir la pieza.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p03.png`

**Tip K3D:** si la boquilla deja una marca sobre la cama o el filamento sale aplastado, el Z-offset puede estar demasiado bajo.

---

## 3. La pieza no se pega a la cama

**Cómo se ve:** la primera capa se despega, se arrastra con la boquilla o las esquinas se levantan.

**Causas posibles:**
- cama sucia con grasa o polvo;
- mala nivelación;
- Z-offset muy alto;
- temperatura de cama baja;
- velocidad de primera capa muy alta;
- poca superficie de contacto del modelo.

**Soluciones recomendadas:**
1. Limpia la cama con alcohol isopropílico, si el tipo de superficie lo permite.
2. Recalibra la cama o ajusta el Z-offset.
3. Sube ligeramente la temperatura de cama según el material.
4. Activa **Brim** si la pieza tiene poca base.
5. Reduce la velocidad de primera capa.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p04.png`

**Recomendación:** para PLA, una cama entre 50 °C y 60 °C suele funcionar bien como punto de partida.

---

## 4. Hilos entre partes del modelo / Stringing

**Cómo se ve:** aparecen hilos finos de filamento entre zonas separadas de la pieza.

**Causas posibles:**
- temperatura demasiado alta;
- retracción insuficiente;
- filamento húmedo;
- velocidad de viaje baja;
- material muy fluido.

**Soluciones recomendadas:**
1. Baja la temperatura de boquilla en pasos de 5 °C.
2. Ajusta la retracción según el tipo de extrusor.
3. Seca el filamento si estuvo expuesto a humedad.
4. Aumenta la velocidad de movimiento o travel.
5. Activa opciones de evitar cruces sobre perímetros si el laminador lo permite.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p05.png`

**Tip K3D:** en equipos Bambu, primero prueba con el perfil estándar del material antes de tocar muchos parámetros manualmente.

---

## 5. Warping o esquinas levantadas

**Cómo se ve:** las esquinas de la pieza se levantan y la base se deforma.

**Causas posibles:**
- mala adhesión de primera capa;
- contracción del material;
- corrientes de aire;
- cama con temperatura insuficiente;
- pieza grande con base extensa.

**Soluciones recomendadas:**
1. Limpia la cama y revisa el Z-offset.
2. Usa Brim para aumentar la superficie de adhesión.
3. Evita corrientes de aire durante la impresión.
4. Usa impresora cerrada o enclosure para ABS/ASA.
5. Ajusta temperatura de cama según el material.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p06.png`

---

## 6. Capas desplazadas

**Cómo se ve:** una parte de la impresión aparece corrida hacia un lado.

**Causas posibles:**
- correas flojas;
- poleas mal ajustadas;
- choque de la boquilla contra la pieza;
- velocidad o aceleración demasiado alta;
- motor perdiendo pasos.

**Soluciones recomendadas:**
1. Revisa tensión de correas.
2. Verifica que la pieza esté bien adherida a la cama.
3. Reduce velocidad/aceleración si el perfil es muy agresivo.
4. Revisa que no haya obstáculos en los ejes.
5. Evita soportes o bordes que puedan golpear la boquilla.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p07.png`

---

## 7. Subextrusión

**Cómo se ve:** capas débiles, líneas separadas, paredes incompletas o huecos entre pasadas.

**Causas posibles:**
- boquilla parcialmente obstruida;
- temperatura baja;
- filamento con diámetro irregular;
- extrusor sucio o con poca presión;
- velocidad demasiado alta para el flujo disponible.

**Soluciones recomendadas:**
1. Sube la temperatura de boquilla en pasos de 5 °C.
2. Reduce velocidad de impresión.
3. Limpia boquilla y engranaje del extrusor.
4. Revisa que el filamento corra libremente.
5. Cambia la boquilla si está muy gastada u obstruida.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p08.png`

---

## 8. Sobreextrusión

**Cómo se ve:** exceso de material, bordes abultados, capas muy gruesas o detalles deformados.

**Causas posibles:**
- flujo demasiado alto;
- temperatura alta;
- perfil incorrecto de material;
- boquilla o diámetro configurado incorrectamente.

**Soluciones recomendadas:**
1. Verifica que la boquilla configurada coincida con la real.
2. Reduce flujo o extrusion multiplier si el laminador lo permite.
3. Baja temperatura en pasos de 5 °C.
4. Usa un perfil estándar del material como punto de partida.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p09.png`

---

## 9. Soportes difíciles de retirar

**Cómo se ve:** los soportes se pegan demasiado a la pieza o dejan marcas fuertes.

**Causas posibles:**
- distancia Z de soporte muy baja;
- densidad de soporte alta;
- orientación poco favorable;
- temperatura alta;
- tipo de soporte no adecuado.

**Soluciones recomendadas:**
1. Reorienta el modelo para reducir soportes.
2. Usa soporte tipo árbol si conviene.
3. Reduce densidad de soporte.
4. Aumenta la distancia entre soporte y pieza si el laminador lo permite.
5. Usa interfaces de soporte solo cuando sean necesarias.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p10.png`

---

## 10. Mala calidad superficial

**Cómo se ve:** líneas muy visibles, vibraciones, marcas, superficie irregular o detalles poco definidos.

**Causas posibles:**
- altura de capa muy alta;
- velocidad excesiva;
- vibración mecánica;
- temperatura incorrecta;
- filamento húmedo.

**Soluciones recomendadas:**
1. Usa altura de capa menor si buscas más detalle.
2. Reduce velocidad para piezas estéticas.
3. Revisa correas, ruedas y estabilidad de la máquina.
4. Ajusta temperatura según material.
5. Seca el filamento si hay burbujas o textura irregular.

**[IMAGEN SUGERIDA]** `imagenes/errores/errores_p11.png`

---

## 11. Checklist rápido antes de pedir soporte

Antes de contactar a soporte, recopila:

- foto de la pieza fallida;
- foto de la primera capa;
- material usado;
- temperatura de boquilla y cama;
- modelo de impresora;
- software usado;
- captura de parámetros principales;
- video corto si el problema ocurre durante la impresión.

**CTA sugerido:** `Contactar soporte técnico por WhatsApp`
