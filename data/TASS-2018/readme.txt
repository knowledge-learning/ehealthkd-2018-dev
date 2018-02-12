Anotación de Acciones entre Entidades.

El objetivo de esta tarea es anotar la presencia de conceptos y acciones en una oración.
En primer lugar es necesario anotar los conceptos.
Un concepto es cualquier elemento de la oración sobre el cuál se menciona un hecho.

El asma afecta las vías respiratorias.

Luego se anotan las acciones.
Una acción también es un concepto, que describe una transformación o modificación del estado de uno o más conceptos presentes en la oración.
Una acción puede ser realizada por un sujeto (Subject) sobre un objetivo (Target).
El sujeto es quien ejecuta la acción, y el objetivo es quen recibe los efectos de dicha acción.
El ejemplo más básico es cuando se describe directamente un concepto realizando una acción sobre otro concepto.

El asma afecta las vías respiratorias.

Las acciones pueden ser reflexivas, cuando son realizadas por el mismo concepto que recibe el efecto.
En este caso, tanto el sujeto como el objetivo son el mismo concepto.

Los pulmones se hinchan.

También pueden ser acciones pasivas, cuando no se expresa quién realiza la acción, pero se sabe quién recibe el efecto de la misma.

Es díficil diagnosticar el cáncer de pulmón.

Además de acciones, existen relaciones entre los conceptos. Los tipos de relaciones son:
(is-a): cuando un concepto es un tipo más concreto que otro concepto.

El asma es una enfermedad.

(part-of): cuando un concepto forma parte de otro concepto (composición, está contenido, etc.):

En los bronquios, que son parte de su sistema respiratorio...

(property-of): cuando un concepto sirve para indicar propiedades o atributos de otro concepto. Generalmente se usa junto a varias relaciones is-a:

Los síntomas del asma son: tos, falta de aire, ...

(same-as): cuando dos conceptos se refieren unívocamente al mismo concepto:

Un tumor maligno (también denominado cáncer) es...

Tanto el sujeto como el objeto de una acción pueden ser a su vez acciones realizadas por otros sujetos.
De esta forma se describe una composición, en la cuál el hecho de realizar una acción se ve como un concepto en sí.

Un ataque de asma se produce cuando los síntomas empeoran.

Por ejemplo, en la oración anterior, primero detectamos el concepto "síntomas" y la acción "empeoran".
Esta acción no tiene sujeto pues no se indica quién es el responsable del empeoramiento.
Luego reconocemos el concepto "ataque de asma" y la acción produce.
El sujeto de la acción "produce" es el concepto complejo denotado por el "empeoramiento de los síntomas", y el objetivo es el ataque de asma.

Si vemos la oración anterior dicha de otro modo, estaríamos reconociendo exactamente el mismo conocimiento, aunque el orden las palabras cambie, e incluso cambie la función gramatical de cada palabra.
Recordemos que definimos acción como un concepto que indica una transformación o cambio de estado, no necesariamente tiene que ser indicado por un verbo. También puede ser indicado por un sustantivo (o un sintagma nominal en general) si lo que se expresa es una transformación.

El empeoramiento de los síntomas produce un ataque de asma.

Las acciones pueden estar tener un atributo (^) Negated cuando están siendo negadas, y un atributo Uncertain (?) cuando existe incertidumbre:

Estas células adicionales pueden formar un tumor.
Las células cancerígenas no mueren.

Cuando un mismo fragmento del texto sirve para indicar más de acción, o una misma acción entre varios pares de sujetos y objetos, se añade una anotación por cada instancia de la acción que se necesite:

Los síntomas y el tratamiento dependen del tipo de cáncer y de lo avanzada que esté la enfermedad.

A veces puede existir un concepto derivado (is-a) de otro concepto, en la misma frase:

Un profesional de la salud puede ...

Algunas veces uan misma frase puede ser etiquetada con (is-a) o con (property-of):

Los profesionales sugieren asesoría psicológica.

Los profesionales sugieren asesoría psicológica.

En este caso, siempre elegiremos (is-a) si necesitamos adicionar una relación al concepto que estaría siendo denotado por la propiedad:

Los profesionales sugieren asesoría psicológica.

En el caso anterior como necesitamos asignar como "target" a la frase "asesoría psicológica", la convertimos en un concepto y usamos una relación (is-a).
En caso de que no hiciera falta asociarle ninguna relación, o en caso de que el concepto en sí tenga un significado propio, se anota como (property-of).

Un profesional con licencia.
