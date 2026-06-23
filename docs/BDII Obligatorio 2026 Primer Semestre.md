Página 1 de 8 

Bases de Datos II 

## **BDII - Trabajo obligatorio 2026** 

Con el Mundial 2026 a la vuelta de la esquina, ya falta menos para comenzar a alentar a nuestra celeste de corazón. Mientras en USA, Canadá y México hacen los aprontes de infraestructura para la organización de los eventos de juego, que tendrán lugar en los distintos estadios, la UCU fue elegida para desarrollar un sistema integral de _Ticketing_ para la comercialización, transferencia y validación de entradas en estos eventos de alta concurrencia – los partidos del mundial. A diferencia de los sistemas de _ticketing_ tradicionales, esta plataforma implementa un modelo de Entrada Dinámica, donde el activo digital no es una imagen estática, sino un token que muta periódicamente para evitar el fraude y la reventa no autorizada, manteniendo siempre un registro histórico de su cadena de custodia. 

Luego de varias reuniones de coordinación, se relevaron los siguientes requerimientos del sistema a implementar. 

Se contará con un módulo centralizado de usuarios donde se gestionará lo siguiente. 

## **Registro y Perfiles** 

1. **Registro:** Los usuarios podrán registrarse proporcionando sus datos personales, incluyendo su mail que lo identifica, documento que se compone del País, Tipo de Documento y Numero que es único, la dirección (compuesta de País, Localidad, Calle, Numero y Código Postal). Además, podrán registrar múltiples teléfonos de contacto. Cada cuenta será única y servirá como el "repositorio" de sus activos digitales. 

2. **Perfiles:** Se deberá implementar un control de acceso basado en roles. Con este enfoque se contará con los siguientes roles: 

   - **Administrador por País Sede:** Tendrá facultades para gestionar los estadios y eventos asignados exclusivamente a su jurisdicción geográfica. De los administradores se desea registrar la Fecha de asignación al cargo. 

   - **Funcionario de Validación:** Es de un perfil técnico/operativo vinculado a un dispositivo físico para el control de accesos en los estadios. De estos funcionarios se desea registrar Número de legajo. 

   - **Usuario General:** Orientado al consumidor final para compra, recepción y transferencia de entradas. De estos se registra la fecha de registro en el sistema, y estado de verificación de la identidad. 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Bases de Datos II Página 2 de 8 

## **Administración de Infraestructura y Eventos** 

El núcleo operativo de la aplicación reside en la configuración precisa de los escenarios y los encuentros deportivos. 

1. **Gestión de Estadios:** Se requiere un módulo para la definición de recintos, donde cada estadio se desglosará en Sectores (A, B, C, D). Cada sector tendrá una capacidad máxima parametrizable, actuando como un límite duro para la emisión de entradas y evitando el sobre aforo. El costo de cada entrada varía por sector. 

2. **Configuración de Eventos:** El sistema permitirá programar los encuentros definiendo los equipos participantes (local/visitante), vinculándolos a un estadio específico y asignando una fecha y hora exacta. La lógica de negocio debe impedir la superposición de eventos en un mismo recinto. El Administrador es quien da de alta estos eventos. 

Además, para cada evento se habilitan uno o más sectores del estadio. 

## **Proceso de Venta y Distribución de entradas** 

La venta de entradas se gestionará de forma centralizada, pero con una estructura de datos flexible. Todas las operaciones de venta podrán contener múltiples entradas, permitiendo al usuario adquirir boletos para diferentes sectores o múltiples entradas para un mismo sector en una única transacción. Aunque una venta genere varias entradas, cada boleto individual tendrá su propio identificador único en la base de datos, quedando inicialmente bajo la titularidad del usuario comprador. 

De cada venta se registra la fecha, estado (pendiente, confirmada, paga) y monto total, calculado en base al costo de cada entrada más una comisión del 5% sobre el total, se debe tener en cuenta que esta taza puede variar a lo largo del tiempo. Un usuario no puede comprar más de 5 entradas en la misma transacción. 

## **Uno de los pilares del sistema es el desacoplamiento entre la compra y la tenencia de la entrada.** 

Inicialmente, todas las entradas quedan asociadas al usuario comprador. El sistema permitirá que un usuario transfiera una entrada a otro de forma directa dentro de la plataforma. Una vez el usuario destinatario acepte la transferencia, la entrada cambiara de propietario. El sistema deberá mantener un log histórico de cada transferencia, permitiendo reconstruir el camino de una entrada desde su emisión original hasta su validación final en puerta. Una entrada puede ser transferida como máximo 3 veces antes de su validación. 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Página 3 de 8 

Bases de Datos II 

## **Seguridad y Validación de Acceso a eventos** 

Por reglamentación de la FIFA el sistema ha de ser muy meticuloso con los asuntos de seguridad y para prevenir la falsificación de entradas por captura de pantalla, se requiere que el sistema implemente un mecanismo de QR Dinámico. 

## **1. Seguridad de acceso** 

- **Generación de Tokens:** Mientras la aplicación esté en primer plano, el código QR de la entrada se regenerará cada 30 segundos. Esto garantiza que solo quien posee la aplicación activa puede ingresar. 

- **Dispositivos de Escaneo Autorizados:** No cualquier dispositivo podrá validar entradas. Se gestionará un registro de IDs de Dispositivos autorizados, los cuales deben estar vinculados obligatoriamente a un funcionario a cargo. 

## **2. Validación de acceso** 

- **Validación y Auditoría:** Al momento del escaneo, el sistema verificará la validez del QR activo y registrará no solo el ingreso, sino también el código específico que fue aceptado y la identidad del funcionario que realizó la operación de validación, marcando la entrada como "consumida" de forma irreversible. Un funcionario debe haber validado entradas en todos los sectores a los que fue asignado durante un evento. 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Página 4 de 8 

Bases de Datos II 

## **¿Cómo funcionaría?** 

Empecemos por registrarnos y realizar la compra de entradas para los partidos (como se indicó previamente no podré comprar más de 5 entradas en la misma transacción). Se deberá otorgar a cada usuario la posibilidad de ver sus compras ingresadas, las transferencias realizadas y las entradas que actualmente tiene asignadas. 

La funcionalidad mínima es la de poder registrarse, comprar entradas, transferir entradas, todo lo relativo al registro de eventos, funcionalidades para la validación de ingreso a los eventos, listar las compras y transferencias de entradas efectuadas por cada usuario, así como las entradas que tiene cada uno asignadas. También se debería visualizar los eventos en los que se vendieron más entradas y el ranking de los mayores compradores. 

## **Otras consideraciones** 

Esta aplicación deberá poder ser usada inicialmente por todos los alumnos de la UCU que se hayan registrado en la misma. El Sistema debe tener en cuenta que a futuro puede interesar sacar estadísticas de los eventos (partidos) para los cuales se vendieron más entradas, así como los usuarios que son mayores compradores de entradas, por ejemplo. 

Las funcionalidades de esta _app_ estarán limitadas solo por su imaginación, y en ello residirá el valor que tenga. Mínimamente deberá contemplar factores como los descriptos previamente, multiusuario, obviamente que, en una base de datos, programado con SQL. 

Se le pide que investigue con las personas de su grupo cómo se podría resolver este problema. Luego de ello, modélelo, todo lo que el problema representa, sus desafíos y la lógica necesaria que tiene para funcionar, arme la base de datos que se necesitaría. 

Una vez lograda la base de datos, trabaje en elaborar la aplicación, considere que será un prototipo por lo que debería ser posible que sea extensible para mayores funcionalidades. ¿Su modelo es capaz de hacerlo con facilidad? 

Se les pide que investiguen qué base de datos y qué lógica debería dar sustento a los programas de las características solicitadas. 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Bases de Datos II Página 5 de 8 

## **Pautas generales de trabajo** 

## _**Entregas**_ 

El trabajo deberá estar implementado en una base de datos que soporte SQL, quedando el estudiante en libertad de elegir la base de datos, previa justificación. La base de datos debe residir en Linux. Su aplicación deberá trabajar en modalidad “Cliente/Servidor”. 

El lenguaje de programación deberá ser alguno de los soportados por .NET o bien en Java. Si pretende utilizar otro lenguaje, consulte previamente para obtener un visto bueno de la Cátedra. Independientemente del lenguaje y base de datos que se seleccione, la implementación deberá ser hecha en SQL. También queda en libertad de elegir la plataforma en que ejecute la aplicación. 

Se recomienda recurrir a la bibliografía y artículos aportados en el curso; asimismo se recomienda la evaluación de productos disponibles en el mercado de forma tal de aprovechar posibles ideas y elementos implementados en dichas herramientas. 

## _**Requerimientos obligatorios**_ 

El trabajo consiste en un análisis profundo de un problema durante un par de meses, donde el equipo está a cargo de la investigación y el desarrollo de una versión “demo” del sistema que se describe anteriormente. La versión de la aplicación debe incluir **obligatoriamente** todos los requerimientos listados durante el desarrollo del problema. Cualquier bug NO funcional es aceptable siempre y cuando cuente con la debida justificación. 

## _**Requerimientos opcionales**_ 

- Funcionales 

   - Implementación y escaneo de códigos QR 

   - Reportes estadísticos del lado del administrador 

- Implementación 

   - Optimización del modelo físico 

   - Utilización de índices y otras herramientas para mejorar performance 

   - Utilización de Docker 

   - Alta disponibilidad y escalabilidad futura de la aplicación 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Página 6 de 8 

Bases de Datos II 

## _**Entregables**_ 

El _**informe del trabajo**_ deberá contar con: 

- Un resumen de la información teórica utilizada (con un máximo de 30 hojas); 

- Un conjunto mínimo de tres alternativas que podrían dar solución al problema (tanto funcionales como de datos), con su discusión; 

- La elección de la alternativa a ser implementada, debidamente justificada. 

- La implementación de dicha alternativa, documentando: 

   - Evolución del MER (3 versiones incluyendo la final) 

   - el modelo de datos final (MER, Modelo Lógico, scripts de creación de la base de datos) 

   - la funcionalidad de este (diagrama de componentes, clases, colaboración, algoritmos, etc.) 

- Breve capítulo de conclusiones, en el cual se pueda resumir los aspectos más importantes del trabajo, cuáles son los próximos pasos, o aquellos aspectos relevantes que se deseen concluir. 

El tamaño total del informe no puede exceder las 50 páginas, no se aceptarán trabajos que no cumplan con este requisito. 

La documentación teórica debe contener las referencias a las fuentes de donde tomó la información (con referencias en los párrafos correspondientes) y en caso de incluir texto literal de alguna fuente **DEBEN** hacerlo correctamente, utilice las normas APA (https://normasapa.com). 

El _**ejecutable**_ deberá ser acompañado de la documentación necesaria para comprender su forma de trabajo y la manera de ejecutarlo. En el caso que hayan ocurrido variaciones entre la implementación presentada en el informe del trabajo y la confección del ejecutable se deberá agregar un anexo que indique los cambios efectuados. Los únicos cambios aceptables son aquellos que involucren cambios en la implementación de la solución presentada y no en la solución propiamente dicha. 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Página 7 de 8 

Bases de Datos II 

## **Consideraciones importantes de las entregas** 

- El código de la aplicación debe estar **obligatoriamente en GitHub en un repositorio público** 

- Los entregables deberán ser subidos a WebAsignatura (Informe PDF, ZIP del código y URL del repositorio de GitHub). 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

Página 8 de 8 

Bases de Datos II 

**Reglas de colaboración** : El obligatorio es en grupo de 3 personas, los integrantes son los responsables de la división del trabajo en forma equitativa. El trabajo debe ser original, producido enteramente por ustedes. 

**Entregas tardías:** No es posible entregar el obligatorio después de fecha. 

**Entregas por email:** No se aceptarán entregas por email excepto que Web Asignatura no esté disponible seis horas antes a la fecha final de entrega. La entrega por email debe enviarse a **todos** los profesores y pedirles confirmación de entrega. Es su responsabilidad asegurarse que el trabajo haya sido recibido. 

**Valuación:** La entrega será evaluada y se asignará una nota a cada uno de los estudiantes, pudiéndose tomar defensas orales y/o escritas en el caso que los profesores lo consideren necesario. La no presentación a las defensas provocará que el alumno no pueda ser evaluado y, por ende, será calificado con D (deficiente). 

**Entrega de la Letra: 15/4/2026 Entrega del MER: 18/05/2026 Entrega del Informe: 22/6/2026 Entrega del Ejecutable: 24/6/2026 Defensas: 29/06/2026 y 1/7/2026** 

Universidad Católica del Uruguay 

Facultad de Ingeniería y Tecnologías 

