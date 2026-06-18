# Wiki FDM: Guía rápida de Bambu Studio

Aprende el flujo básico para preparar, laminar y enviar un modelo a imprimir usando Bambu Studio.

---

## 1. ¿Qué es Bambu Studio?

Bambu Studio es el software laminador utilizado principalmente con impresoras Bambu Lab. Permite preparar modelos 3D, configurar parámetros de impresión, laminar el archivo, revisar la vista previa y enviar el trabajo directamente a la impresora.

Con Bambu Studio puedes:

- importar archivos STL, 3MF u OBJ;
- seleccionar la impresora y el tipo de filamento;
- configurar calidad, relleno, soportes y adhesión;
- revisar el modelo capa por capa;
- enviar el archivo por red o exportarlo;
- monitorear la impresión desde la pestaña de dispositivo.

**[SCREENSHOT 01: Pantalla principal de Bambu Studio abierta, sin modelo cargado]**

---

## 2. Conoce la interfaz principal

La interfaz de Bambu Studio se divide en zonas clave:

- **Barra superior:** opciones de archivo, configuración, vista y herramientas.
- **Área de trabajo:** cama virtual donde se coloca el modelo.
- **Selector de impresora:** permite elegir el equipo Bambu Lab configurado.
- **Filamento:** muestra el material seleccionado, ya sea desde AMS o spool externo.
- **Proceso:** contiene los parámetros de impresión.
- **Panel de objetos:** permite visualizar modelos, piezas y placas.
- **Botones de acción:** laminar, enviar, imprimir o exportar.

**[SCREENSHOT 02: Interfaz de Bambu Studio con zonas marcadas: impresora, filamento, proceso, área de trabajo y botones]**

**Tip K3D:** Antes de laminar, verifica siempre que la impresora, la boquilla y el filamento seleccionado coincidan con tu equipo real.

---

## 3. Seleccionar o agregar tu impresora

Antes de preparar un archivo, debes seleccionar el modelo de impresora correcto.

Pasos:

1. Abre Bambu Studio.
2. Ingresa a la sección de impresoras.
3. Selecciona tu modelo: A1, A1 mini, P1S, P1P, X1 Carbon, H2S, H2D u otro compatible.
4. Verifica el tamaño de boquilla, normalmente 0.4 mm.
5. Guarda la configuración.

**[SCREENSHOT 03: Ventana de selección o configuración de impresora en Bambu Studio]**

**Recomendación:** Si el cliente tiene AMS, verifica que el sistema reconozca correctamente los filamentos cargados.

---

## 4. Configurar el filamento

El filamento seleccionado en Bambu Studio debe coincidir con el material que usarás en la impresora.

Pasos:

1. Selecciona el material correspondiente: PLA, PETG, ABS, TPU, ASA, etc.
2. Si usas AMS, revisa que el color y tipo de filamento sean correctos.
3. Si usas spool externo, selecciona el material manualmente.
4. Verifica que el perfil de temperatura sea adecuado.

**[SCREENSHOT 04: Panel de filamento en Bambu Studio mostrando PLA seleccionado]**

**Tip K3D:** Si usas filamentos de terceros, puedes seleccionar un perfil genérico y ajustar temperatura según la etiqueta del filamento.

---

## 5. Importar un modelo STL, 3MF u OBJ

Para cargar un modelo:

1. Haz clic en **Importar** o arrastra el archivo al área de trabajo.
2. Selecciona tu archivo STL, 3MF u OBJ.
3. Espera a que el modelo aparezca sobre la placa.
4. Verifica que esté dentro del volumen de impresión.

**[SCREENSHOT 05: Botón de importar archivo o archivo siendo arrastrado a Bambu Studio]**

**[SCREENSHOT 06: Modelo cargado sobre la placa de impresión]**

**Recomendación:** Si el modelo aparece fuera de la placa o demasiado grande, usa las herramientas de mover, rotar o escalar.

---

## 6. Herramientas básicas del modelo

Bambu Studio permite ajustar el modelo antes de laminar.

### Mover

Permite cambiar la posición del modelo sobre la placa.

**[SCREENSHOT 07: Herramienta Mover activa sobre un modelo]**

### Escalar

Permite aumentar o reducir el tamaño del modelo.

**[SCREENSHOT 08: Herramienta Escalar activa con porcentaje visible]**

### Rotar

Permite cambiar la orientación del modelo para mejorar la impresión.

**[SCREENSHOT 09: Herramienta Rotar activa con ejes visibles]**

### Organizar automáticamente

Permite acomodar uno o varios modelos dentro de la placa.

**[SCREENSHOT 10: Botón Organizar / Auto-arrange con varios modelos en la placa]**

**Tip K3D:** Una buena orientación puede reducir soportes, mejorar el acabado y disminuir el tiempo de impresión.

---

## 7. Configurar los parámetros principales

En Bambu Studio, los parámetros de impresión se encuentran en el área de **Proceso**.

### Calidad

Define la altura de capa y el nivel de detalle.

Valores recomendados:

- **0.12 mm:** mayor detalle, más tiempo.
- **0.20 mm:** equilibrio recomendado.
- **0.28 mm:** más rápido, menor detalle.

**[SCREENSHOT 11: Panel Proceso > Calidad / Layer Height]**

### Resistencia / Strength

Define paredes, capas superiores/inferiores y relleno.

Valores recomendados:

- **2 paredes:** piezas decorativas o simples.
- **3 paredes:** uso general.
- **15% a 20% de relleno:** recomendado para piezas comunes.
- **30% o más:** piezas funcionales o resistentes.

**[SCREENSHOT 12: Panel Proceso > Strength / Relleno y paredes]**

### Soportes

Activa soportes cuando el modelo tenga partes suspendidas o ángulos pronunciados.

Opciones comunes:

- Soporte normal.
- Soporte tipo árbol.
- Soporte solo desde la placa.
- Soporte automático.

**[SCREENSHOT 13: Panel Proceso > Soportes activados]**

### Adhesión a la placa

Ayuda a que la pieza se mantenga pegada durante la impresión.

Opciones comunes:

- **Skirt:** línea de purga alrededor del modelo.
- **Brim:** borde adherido a la pieza para mejorar agarre.
- **Raft:** base completa, solo para casos específicos.

**[SCREENSHOT 14: Parámetros de adhesión / Brim activado]**

---

## 8. Trabajar con varias placas

Bambu Studio permite trabajar con varias placas dentro del mismo proyecto. Esto es útil cuando tienes varias piezas o quieres organizar diferentes impresiones.

Pasos:

1. Agrega una nueva placa.
2. Coloca modelos distintos en cada placa.
3. Lamina una placa específica o todas las placas.
4. Envía a imprimir la placa que corresponda.

**[SCREENSHOT 15: Proyecto con varias placas visibles en Bambu Studio]**

**Recomendación:** Usa varias placas cuando el modelo tenga muchas piezas o cuando quieras separar impresiones por color, material o tiempo.

---

## 9. Laminar el modelo

Cuando el modelo y los parámetros estén listos, debes laminar.

Pasos:

1. Haz clic en **Slice Plate** o **Laminar placa**.
2. Espera a que Bambu Studio procese el archivo.
3. Revisa el tiempo estimado.
4. Revisa el consumo de filamento.
5. Pasa a la vista previa.

**[SCREENSHOT 16: Botón Slice Plate / Laminar placa]**

Bambu Studio permite laminar una placa o todas las placas del proyecto, según cómo esté organizado el archivo.

---

## 10. Revisar la vista previa

La vista previa permite revisar cómo se imprimirá el modelo capa por capa.

Verifica:

- que la primera capa esté completa;
- que los soportes estén donde corresponde;
- que no haya partes flotando;
- que el relleno sea adecuado;
- que el tiempo y consumo de material sean razonables;
- que no existan errores visibles antes de enviar.

**[SCREENSHOT 17: Vista Preview con capas visibles]**

**[SCREENSHOT 18: Vista Preview mostrando soportes y trayectorias de impresión]**

**Tip K3D:** Nunca envíes a imprimir sin revisar la vista previa. Muchos errores se pueden detectar antes de gastar material.

---

## 11. Enviar a imprimir

Una vez laminado el modelo, puedes enviarlo a la impresora.

Pasos generales:

1. Haz clic en **Print** o **Imprimir**.
2. Selecciona la impresora disponible.
3. Confirma las opciones de calibración.
4. Verifica el filamento seleccionado.
5. Envía el trabajo a la impresora.

**[SCREENSHOT 19: Ventana de envío a impresión con impresora seleccionada]**

En Bambu Studio, también puedes usar opciones como enviar el archivo a la impresora o exportar el archivo, dependiendo del modelo y conexión disponible.

**[SCREENSHOT 20: Botones Print / Send / Export en Bambu Studio]**

**Nota K3D:** Si la impresora no aparece, revisa que esté conectada a la misma red, vinculada a la cuenta correcta y con tarjeta microSD instalada si corresponde.

---

## 12. Monitorear la impresión

La pestaña de dispositivo permite revisar el estado de la impresora.

Desde esta zona puedes visualizar:

- progreso de impresión;
- temperatura de boquilla;
- temperatura de cama;
- estado del AMS;
- cámara, si el modelo la incluye;
- pausas o cancelación del trabajo;
- historial o trabajos recientes.

**[SCREENSHOT 21: Pestaña Device / Dispositivo con impresora conectada]**

**Recomendación:** Durante la primera impresión, revisa especialmente la primera capa. Una mala primera capa puede causar fallas durante toda la impresión.

---

## 13. Perfil inicial recomendado para PLA

Para usuarios nuevos, puedes iniciar con estos valores:

| Parámetro | Valor sugerido |
|---|---:|
| Material | PLA |
| Boquilla | 0.4 mm |
| Altura de capa | 0.20 mm |
| Relleno | 15%–20% |
| Paredes | 2–3 |
| Soportes | Solo si el modelo lo requiere |
| Brim | Solo si hay poca adherencia |
| Velocidad | Perfil estándar del equipo |

**[SCREENSHOT 22: Perfil PLA básico seleccionado en Bambu Studio]**

**Tip K3D:** En equipos Bambu Lab, los perfiles estándar suelen funcionar bien para primeras impresiones. Ajusta parámetros solo cuando ya entiendas qué resultado quieres mejorar.

---

## 14. Checklist antes de imprimir

Antes de enviar el archivo, revisa:

- la impresora seleccionada es la correcta;
- el filamento coincide con el material real;
- el modelo está dentro de la placa;
- el modelo está bien orientado;
- se activaron soportes si eran necesarios;
- revisaste la vista previa;
- la placa de impresión está limpia;
- el AMS o spool externo tiene suficiente filamento.

**[SCREENSHOT 23: Checklist visual o captura general antes de imprimir]**

---

## 15. Errores comunes al usar Bambu Studio

### La impresora no aparece

Posibles causas: impresora apagada, otra red, cuenta no vinculada, problema de conexión o modo LAN.

Solución recomendada: verifica WiFi, revisa Bambu Handy, reinicia Bambu Studio y confirma que la impresora esté vinculada correctamente.

### No permite enviar el archivo

Posibles causas: filamento seleccionado no coincide, impresora no conectada, falta tarjeta microSD, modelo no laminado o error de red.

Solución recomendada: revisa impresora y filamento, vuelve a laminar, revisa conexión o exporta el archivo como alternativa.

### El modelo necesita muchos soportes

Posibles causas: mala orientación, pieza con voladizos o geometría compleja.

Solución recomendada: rota el modelo, usa soportes tipo árbol, prueba soporte solo desde la placa o divide el modelo si es necesario.

---

## Soporte Krear 3D

Si necesitas ayuda, envíanos fotos o videos del caso para poder orientarte mejor.

**Soporte técnico vía WhatsApp:** +51 970 539 751  
**Atención únicamente por chat.**
