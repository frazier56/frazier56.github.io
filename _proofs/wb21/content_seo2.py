# -*- coding: utf-8 -*-
"""SEO re-aim batch (24 Nov 2026): service + city pages for what people actually search
(tour guide, event host / MC, model, builder / contractor in Medellín) and three topic guides
(things to do and events, furnished and short-term rentals, buying a home and owner financing).

Same truth rules as content.py:
- Prices only where a public source exists and is named. Where none exists (event host, model),
  the page says so and prints no number.
- No "verified" pros, no invented members, reviews or counts. OneJob is new in Medellín, so these
  pages invite pros to join and never imply listings that are not there.
- Not built here: "private security". It is a regulated activity in Colombia (Decreto-Ley 356 de
  1994 requires a licence from the Superintendencia de Vigilancia y Seguridad Privada) and needs
  counsel before we publish advice or a hire flow.
"""

NEW_S = {
 "tbl": ("Tours by Locals — Medellín private tours", "https://www.toursbylocals.com/tours/colombia/medellin", "booking site, prices in US dollars, read 24 Nov 2026", "sitio de reservas, precios en dólares, revisado el 24 de nov. de 2026"),
 "oe": ("OneEstimate — Labour price list for construction in Colombia, 2026", "https://oneestimate.ai/es/blog/lista-precios-mano-obra-construccion-colombia-2026", "31 July 2026", "31 de julio de 2026"),
}

JOIN_EN = "OneJob is new in Medellín and the first profiles are still being created. If you do this work, a free profile puts you in front of people searching for it."
JOIN_ES = "OneJob es nuevo en Medellín y los primeros perfiles apenas se están creando. Si usted hace este trabajo, un perfil gratis lo pone frente a quienes lo buscan."

NEW_SERVICES = [
 {
  "slug": "tour-guide",
  "en": {"name": "tour guide", "a": "a tour guide", "h1": "Hire a private tour guide in Medellín",
         "title": "Private tour guide in Medellín: 2026 prices and how to book | One World",
         "desc": "What a private guide-led tour in Medellín costs in 2026 (city, Comuna 13, Guatapé), what is included, and how to agree the day with a local guide through OneJob.",
         "intro": "A half day in the city, Comuna 13, a coffee farm or a full day in Guatapé: here is what private guided tours in Medellín typically cost, what to ask before you book, and how to agree the day through OneJob."},
  "es": {"name": "guía turístico", "a": "un guía turístico", "h1": "Contrate un guía turístico privado en Medellín",
         "title": "Guía turístico privado en Medellín: precios 2026 y cómo reservar | One World",
         "desc": "Cuánto cuesta un tour privado con guía en Medellín en 2026 (ciudad, Comuna 13, Guatapé), qué incluye y cómo acordar el día con un guía local por OneJob.",
         "intro": "Medio día por la ciudad, la Comuna 13, una finca cafetera o un día completo en Guatapé: aquí verá cuánto cuestan normalmente los tours privados con guía en Medellín, qué preguntar antes de reservar y cómo acordar el día por OneJob."},
  "prices": [
   ("Private half-day city tour, 4 to 5 hours (listed per tour, groups of up to 5 or 6)", "about 165 to 181 US dollars", "Tour privado de medio día por la ciudad, 4 a 5 horas (precio por tour, grupos de hasta 5 o 6)", "unos 165 a 181 dólares", "tbl"),
   ("Private full-day tour, 8 hours, city or Guatapé (listed per tour, groups of up to 4 to 6)", "about 245 to 362 US dollars", "Tour privado de día completo, 8 horas, ciudad o Guatapé (precio por tour, grupos de hasta 4 a 6)", "unos 245 a 362 dólares", "tbl"),
  ],
  "note_en": "These are packaged private tours on one booking site, listed with the maximum group size shown and \"all fees\" included; the site does not say whether the price is per group or per person, so confirm that with the guide. They are not hourly guide rates. " + JOIN_EN,
  "note_es": "Son tours privados empaquetados en un sitio de reservas, publicados con el tamaño máximo del grupo y \"todas las tarifas\" incluidas; el sitio no aclara si el precio es por grupo o por persona, así que confírmelo con el guía. No son tarifas por hora de un guía. " + JOIN_ES,
  "drivers_en": ["Tour length and the route: the city and Comuna 13 are short; Guatapé and El Peñón are a full day each way by road.", "Group size, and whether the price is per group or per person.", "Transport: is a driver and vehicle included, or do you arrange it?", "Entrance fees, lunch and cable-car tickets: included or extra?", "Guide languages (English, Spanish, others) and how much the guide knows about the area."],
  "drivers_es": ["Duración y ruta: la ciudad y la Comuna 13 son cortas; Guatapé y El Peñón son un día completo, con el viaje por carretera.", "Tamaño del grupo y si el precio es por grupo o por persona.", "Transporte: ¿incluye conductor y vehículo, o usted lo arregla?", "Entradas, almuerzo y tiquetes de metrocable: ¿incluidos o aparte?", "Idiomas del guía (inglés, español, otros) y cuánto conoce la zona."],
  "law_en": "Ask whether the guide is a certified tourist guide and whether the tour operator is registered, and ask what happens if the weather or an attraction closes the day.",
  "law_es": "Pregunte si el guía es un guía de turismo certificado y si el operador está registrado, y qué pasa si el clima o el cierre de un atractivo cambia el plan.",
  "safety": True,
  "faq_en": [("How much does a private tour guide cost in Medellín?", "On one booking site, private guided tours in Medellín are listed at about 165 to 181 US dollars for a half day (4 to 5 hours) and about 245 to 362 US dollars for a full day (8 hours), each with a maximum group size. Prices are per tour as listed; confirm with the guide whether they are per group or per person (Tours by Locals, read 24 November 2026)."),
             ("What are the best tours from Medellín?", "The ones people ask for most are a city tour, Comuna 13, a coffee farm and a full day in Guatapé with El Peñón. Agree the route, the pick-up point and what is included before the day."),
             ("Can I hire a guide and a driver together?", "Yes. Many tours include a driver; if you want a driver only, see the private driver page. Agree in writing who pays entrance fees, parking and meals."),
             ("Does One World check guides?", "No. One World does not run background checks or check certifications. Read the profile and reviews and ask for references.")],
  "faq_es": [("¿Cuánto cuesta un guía turístico privado en Medellín?", "En un sitio de reservas, los tours privados con guía en Medellín aparecen entre unos 165 y 181 dólares por medio día (4 a 5 horas) y entre unos 245 y 362 dólares por un día completo (8 horas), cada uno con un tamaño máximo de grupo. Los precios son por tour; confirme con el guía si son por grupo o por persona (Tours by Locals, revisado el 24 de noviembre de 2026)."),
             ("¿Cuáles son los mejores tours desde Medellín?", "Los que más piden son un tour por la ciudad, la Comuna 13, una finca cafetera y un día completo en Guatapé con El Peñón. Acuerde la ruta, el punto de recogida y lo que incluye antes del día."),
             ("¿Puedo contratar un guía y un conductor juntos?", "Sí. Muchos tours incluyen conductor; si solo quiere un conductor, vea la página de conductor privado. Acuerde por escrito quién paga entradas, parqueadero y comidas."),
             ("¿One World verifica a los guías?", "No. One World no hace verificaciones de antecedentes ni revisa certificaciones. Lea el perfil y las reseñas y pida referencias.")],
 },
 {
  "slug": "event-host",
  "en": {"name": "event host", "a": "an event host or MC", "h1": "Hire an event host or MC in Medellín",
         "title": "Event host and MC in Medellín: how to hire one for your event | One World",
         "desc": "How to hire an event host, MC or animador in Medellín for weddings, corporate events and parties: what to agree, what changes the price and how to book through OneJob.",
         "intro": "Weddings, company events, birthdays and launches: a good host keeps the night moving. Here is what to agree with an event host or MC in Medellín and how to book one through OneJob."},
  "es": {"name": "animador", "a": "un animador o presentador de eventos", "h1": "Contrate un animador o presentador de eventos en Medellín",
         "title": "Animador y presentador de eventos en Medellín: cómo contratar | One World",
         "desc": "Cómo contratar un animador o maestro de ceremonias en Medellín para matrimonios, eventos de empresa y fiestas, y cómo reservar por OneJob.",
         "intro": "Matrimonios, eventos de empresa, cumpleaños y lanzamientos: un buen animador mantiene la noche en movimiento. Aquí verá qué acordar con un animador o presentador de eventos en Medellín y cómo reservarlo por OneJob."},
  "prices": [],
  "note_en": "We did not find a public price range for event hosts or MCs in Medellín that we trust, so we are not printing a number. Ask for quotes per event and per hour, and compare at least three. " + JOIN_EN,
  "note_es": "No encontramos un rango de precios público y confiable para animadores o presentadores de eventos en Medellín, así que no publicamos una cifra. Pida cotizaciones por evento y por hora y compare al menos tres. " + JOIN_ES,
  "drivers_en": ["Event type and length: a 3-hour launch and a 6-hour wedding are different jobs.", "Languages: bilingual hosts (Spanish and English) are usually priced higher.", "Preparation: a script, a run-of-show and a meeting with you before the event.", "Extras: working with the DJ, games and activities, microphone and sound.", "Date: December, long weekends and Saturdays book up first."],
  "drivers_es": ["Tipo y duración del evento: un lanzamiento de 3 horas y un matrimonio de 6 son trabajos distintos.", "Idiomas: los animadores bilingües (español e inglés) suelen cobrar más.", "Preparación: guion, programa del evento y una reunión con usted antes.", "Extras: coordinación con el DJ, juegos y actividades, micrófono y sonido.", "Fecha: diciembre, los puentes festivos y los sábados se reservan primero."],
  "faq_en": [("How do I hire an event host in Medellín?", "Decide the event type, date, length and language, then ask for quotes from several hosts, watch a video of them working, and agree the run-of-show and the price in writing. You can search and contract through OneJob."),
             ("What does an MC do at a wedding or corporate event?", "An MC welcomes guests, introduces speakers and moments such as the first dance or the toast, keeps the schedule, and coordinates with the DJ and the venue."),
             ("How much does an event host cost in Medellín?", "We did not find a public price range we trust, so we do not print one. Ask for a quote per event and per hour and compare several."),
             ("Does One World check hosts?", "No. One World does not run background checks. Watch their work, read reviews and ask for references.")],
  "faq_es": [("¿Cómo contrato un animador de eventos en Medellín?", "Defina el tipo de evento, la fecha, la duración y el idioma, pida cotizaciones a varios animadores, vea un video de su trabajo y acuerde por escrito el programa y el precio. Puede buscar y contratar por OneJob."),
             ("¿Qué hace un presentador o maestro de ceremonias en un matrimonio o evento de empresa?", "Da la bienvenida, presenta a los oradores y momentos como el primer baile o el brindis, lleva el cronograma y se coordina con el DJ y el lugar."),
             ("¿Cuánto cuesta un animador de eventos en Medellín?", "No encontramos un rango de precios público y confiable, así que no publicamos una cifra. Pida una cotización por evento y por hora y compare varias."),
             ("¿One World verifica a los animadores?", "No. One World no hace verificaciones de antecedentes. Vea su trabajo, lea las reseñas y pida referencias.")],
 },
 {
  "slug": "model",
  "en": {"name": "model", "a": "a model", "h1": "Hire a model in Medellín for photo and video shoots",
         "title": "Hire a model in Medellín for photo, video and brand shoots | One World",
         "desc": "How to hire a model in Medellín for a photo shoot, video, brand campaign or event: what to agree, image rights and how to book safely through OneJob.",
         "intro": "Product shoots, fashion, real-estate and tourism videos, brand campaigns and events: here is how to hire a model in Medellín, what to agree in writing, and how to book through OneJob."},
  "es": {"name": "modelo", "a": "un modelo", "h1": "Contrate un modelo en Medellín para sesiones de fotos y video",
         "title": "Contratar un modelo en Medellín para fotos, video y campañas | One World",
         "desc": "Cómo contratar un modelo en Medellín para fotos, video, campañas o eventos: qué acordar, derechos de imagen y cómo reservar por OneJob.",
         "intro": "Sesiones de producto, moda, videos inmobiliarios y de turismo, campañas de marca y eventos: aquí verá cómo contratar un modelo en Medellín, qué dejar por escrito y cómo reservar por OneJob."},
  "prices": [],
  "note_en": "We did not find a public price range for models in Medellín that we trust, so we are not printing a number. Rates depend on experience, the type of work and how the images will be used. Ask for a quote per hour or per shoot. " + JOIN_EN,
  "note_es": "No encontramos un rango de precios público y confiable para modelos en Medellín, así que no publicamos una cifra. La tarifa depende de la experiencia, el tipo de trabajo y el uso que se dará a las imágenes. Pida una cotización por hora o por sesión. " + JOIN_ES,
  "drivers_en": ["Type of work: catalogue, fashion, tourism, real estate, commercial or event.", "Usage of the images: web and social media only, or advertising, print and paid ads. Wider use costs more.", "Length of the shoot, and hair, make-up and wardrobe: who provides them?", "Experience and portfolio.", "Travel, outdoor locations and weather."],
  "drivers_es": ["Tipo de trabajo: catálogo, moda, turismo, inmobiliario, comercial o evento.", "Uso de las imágenes: solo web y redes, o publicidad, impresos y pauta pagada. Un uso más amplio cuesta más.", "Duración de la sesión, y peinado, maquillaje y vestuario: ¿quién los pone?", "Experiencia y portafolio.", "Desplazamiento, locaciones al aire libre y clima."],
  "law_en": "Agree the use of the images in writing: where they will appear, for how long and in which countries. Only book adults unless a parent or guardian agrees in writing and is present. Meet in a studio or a public place the first time, and tell someone where the shoot is.",
  "law_es": "Acuerde por escrito el uso de las imágenes: dónde aparecerán, por cuánto tiempo y en qué países. Contrate solo a adultos, salvo que un padre o tutor lo acepte por escrito y esté presente. La primera vez reúnanse en un estudio o en un lugar público y avise a alguien dónde es la sesión.",
  "safety": True,
  "faq_en": [("How do I hire a model in Medellín?", "Say what the shoot is, the date, the length and how the images will be used, then look at portfolios, ask for quotes and agree the details in writing. You can search and contract through OneJob."),
             ("What should a model contract include?", "The date, hours, place, the price, what is provided (make-up, wardrobe, transport), how the images may be used, for how long and where, and what happens if either side cancels."),
             ("How much does a model cost in Medellín?", "We did not find a public price range we trust, so we do not print one. Ask for a quote per hour or per shoot."),
             ("Does One World check models?", "No. One World does not run background checks or verify ages. You are responsible for checking who you book.")],
  "faq_es": [("¿Cómo contrato un modelo en Medellín?", "Diga de qué es la sesión, la fecha, la duración y el uso de las imágenes, luego revise portafolios, pida cotizaciones y acuerde los detalles por escrito. Puede buscar y contratar por OneJob."),
             ("¿Qué debe incluir el contrato de un modelo?", "La fecha, las horas, el lugar, el precio, lo que se provee (maquillaje, vestuario, transporte), cómo se pueden usar las imágenes, por cuánto tiempo y dónde, y qué pasa si alguna de las partes cancela."),
             ("¿Cuánto cuesta un modelo en Medellín?", "No encontramos un rango de precios público y confiable, así que no publicamos una cifra. Pida una cotización por hora o por sesión."),
             ("¿One World verifica a los modelos?", "No. One World no hace verificaciones de antecedentes ni verifica edades. Usted es responsable de revisar a quién contrata.")],
 },
 {
  "slug": "builder",
  "en": {"name": "builder", "a": "a builder or contractor", "h1": "Hire a builder or contractor in Medellín",
         "title": "Builder and contractor in Medellín: 2026 labour prices | One World",
         "desc": "What construction and remodelling labour costs in Medellín in 2026, what to put in the contract, and how to hire a builder through OneJob.",
         "intro": "A remodel, a bathroom, a new floor or a house on your lot: here is what construction labour typically costs in Medellín, what to agree before the first day, and how to hire through OneJob."},
  "es": {"name": "constructor", "a": "un maestro de obra o constructor", "h1": "Contrate un maestro de obra o constructor en Medellín",
         "title": "Maestro de obra en Medellín: precios de mano de obra 2026 | One World",
         "desc": "Cuánto cuesta la mano de obra de construcción y remodelación en Medellín en 2026, qué poner en el contrato y cómo contratar por OneJob.",
         "intro": "Una remodelación, un baño, un piso nuevo o una casa en su lote: aquí verá cuánto cuesta normalmente la mano de obra de construcción en Medellín, qué acordar antes del primer día y cómo contratar por OneJob."},
  "prices": [
   ("Maestro de obra (site foreman), per day", "about 95,000 to 160,000 pesos", "Maestro de obra, por día", "unos 95.000 a 160.000 pesos", "oe"),
   ("Oficial (skilled builder), per day", "about 75,000 to 110,000 pesos", "Oficial de construcción, por día", "unos 75.000 a 110.000 pesos", "oe"),
   ("Ayudante (helper), per day", "about 55,000 to 75,000 pesos", "Ayudante o peón, por día", "unos 55.000 a 75.000 pesos", "oe"),
   ("Interior plastering, per square metre", "about 18,000 to 35,000 pesos", "Revoque interior, por metro cuadrado", "unos 18.000 a 35.000 pesos", "oe"),
   ("Ceramic floor tiling, per square metre", "about 28,000 to 52,000 pesos", "Enchape de piso cerámico, por metro cuadrado", "unos 28.000 a 52.000 pesos", "oe"),
   ("Drywall ceiling, per square metre", "about 28,000 to 55,000 pesos", "Cielo raso en drywall, por metro cuadrado", "unos 28.000 a 55.000 pesos", "oe"),
  ],
  "note_en": "These are labour-only ranges from a single estimating site (31 July 2026). It says the lowest figures are for mid-sized cities and that the top \"specialised\" day rate applies in Bogotá, Medellín and Cali; treat Medellín as the upper half of each range, and ask for a written quote. Materials are extra. " + JOIN_EN,
  "note_es": "Son rangos de solo mano de obra tomados de un único sitio de estimaciones (31 de julio de 2026). Ese sitio indica que las cifras más bajas son para ciudades intermedias y que la tarifa diaria más alta, la \"especializada\", aplica en Bogotá, Medellín y Cali; tome Medellín como la mitad alta de cada rango y pida una cotización por escrito. Los materiales van aparte. " + JOIN_ES,
  "drivers_en": ["Day rate or price per square metre: agree which, and what is measured.", "Materials: who buys them and who is responsible for waste and delivery.", "Experience and the size of the crew.", "Access, floor level and demolition or cleanup.", "Structural work, extensions or new builds: these usually need plans and a permit, and a professional such as an architect or engineer."],
  "drivers_es": ["Jornal o precio por metro cuadrado: acuerde cuál y qué se mide.", "Materiales: quién los compra y quién responde por escombros y transporte.", "Experiencia y tamaño de la cuadrilla.", "Acceso, piso del inmueble, demolición y limpieza.", "Obras estructurales, ampliaciones o casas nuevas: suelen requerir planos y licencia, y un profesional como arquitecto o ingeniero."],
  "law_en": "Before structural work, ask who obtains the building permit (licencia de construcción) and who is responsible for the plans. Ask who pays the workers' social security and insurance, agree the payment schedule in stages tied to finished work, and keep the final payment until the job is complete. This is general guidance, not legal advice.",
  "law_es": "Antes de una obra estructural, pregunte quién tramita la licencia de construcción y quién responde por los planos. Pregunte quién paga la seguridad social y el seguro de los trabajadores, acuerde pagos por etapas ligados a trabajo terminado y deje el último pago para cuando el trabajo esté completo. Es una guía general, no asesoría legal.",
  "safety": True,
  "faq_en": [("How much does a builder cost per day in Medellín?", "One estimating site (31 July 2026) lists about 95,000 to 160,000 pesos a day for a maestro de obra, 75,000 to 110,000 for an oficial and 55,000 to 75,000 for a helper, with Medellín at the higher end. Materials are extra and each builder sets their own price."),
             ("How much does tiling or plastering cost per square metre?", "The same site lists interior plastering at about 18,000 to 35,000 pesos per square metre and ceramic floor tiling at about 28,000 to 52,000, labour only."),
             ("Do I need a permit to remodel in Medellín?", "Structural changes, extensions and new builds usually need a building permit; small interior finishes usually do not. Ask the contractor and, for structural work, an architect or engineer who handles the permit."),
             ("How should I pay a contractor?", "Pay in stages tied to finished work, keep the last payment for completion and put the scope, the schedule and the price in writing. OneJob contracts hold eligible card payments until you both mark the job complete."),
             ("Does One World check builders?", "No. One World does not run background checks or check licences. Ask for references and visit a finished job.")],
  "faq_es": [("¿Cuánto cobra un maestro de obra por día en Medellín?", "Un sitio de estimaciones (31 de julio de 2026) lista unos 95.000 a 160.000 pesos por día para un maestro de obra, 75.000 a 110.000 para un oficial y 55.000 a 75.000 para un ayudante, con Medellín en el extremo alto. Los materiales van aparte y cada constructor fija su precio."),
             ("¿Cuánto cuesta enchapar o pañetar por metro cuadrado?", "El mismo sitio lista el revoque interior en unos 18.000 a 35.000 pesos por metro cuadrado y el enchape de piso cerámico en unos 28.000 a 52.000, solo mano de obra."),
             ("¿Necesito licencia para remodelar en Medellín?", "Los cambios estructurales, ampliaciones y obras nuevas suelen requerir licencia de construcción; los acabados interiores sencillos normalmente no. Pregunte al contratista y, para obras estructurales, a un arquitecto o ingeniero que tramite la licencia."),
             ("¿Cómo debo pagarle a un contratista?", "Pague por etapas ligadas a trabajo terminado, deje el último pago para la entrega y ponga por escrito el alcance, el cronograma y el precio. Los contratos de OneJob retienen los pagos con tarjeta elegibles hasta que ambos marquen el trabajo como terminado."),
             ("¿One World verifica a los constructores?", "No. One World no hace verificaciones de antecedentes ni revisa licencias. Pida referencias y visite una obra terminada.")],
 },
]

# ---------------------------------------------------------------------------------------------
# Topic guides. Same shape as blog_port.POSTS. No prices; no legal claims beyond what is hedged.
# ---------------------------------------------------------------------------------------------
ONEEVENT = "https://app.oneworldlabs.ai/events"
ONEHOME = "https://app.oneworldlabs.ai/home"

NEW_POSTS = [
 {"key": "things-to-do", "slug_en": "things-to-do-in-medellin-events-attractions", "slug_es": "que-hacer-en-medellin-eventos-atracciones", "img": "events.jpg", "city": "tour-guide", "app": ONEEVENT, "new": True,
  "en": {"cat": "Things to do", "title": "Things to do in Medellín: attractions and events | One World Blog",
         "desc": "The attractions people visit in Medellín (Comuna 13, Guatapé, Parque Arví, the city centre) and how to find events, tickets and guides in one place.",
         "h1": "Things to do in Medellín: attractions and events",
         "dek": "What visitors and new residents do first, and where to find what is on this week.",
         "sections": [
          ("Short answer", "<p>Start with a city walk (Plaza Botero and the Museo de Antioquia), a neighbourhood tour in Comuna 13, a Metrocable ride to Parque Arví, and a full day in Guatapé with El Peñón. For nights out, concerts, networking and parties, use OneEvent to see what is on and to buy tickets. Check opening hours and prices on each attraction's own site before you go.</p>"),
          ("Attractions people visit", "<ul><li><strong>City centre:</strong> Plaza Botero, the Museo de Antioquia and Parque Berrío.</li><li><strong>Comuna 13:</strong> a neighbourhood known for its street art, the outdoor escalators and its story of change. Go with a local guide.</li><li><strong>Parque Arví:</strong> a nature park reached by Metrocable above the city.</li><li><strong>Pueblito Paisa and Cerro Nutibara:</strong> a viewpoint and a replica of a traditional town.</li><li><strong>Parque Explora:</strong> a science museum and aquarium.</li><li><strong>Guatapé and El Peñón:</strong> a full-day trip from the city, usually by private car or tour.</li></ul>"),
          ("Events: what is on this week", "<p>On <a href=\"" + ONEEVENT + "\">OneEvent</a> you can browse events in Medellín, buy tickets and check in with a QR code. If you host events, you can list yours and sell tickets in pesos or dollars.</p>"),
          ("Get around and book help", "<p>For a day with a local, see <a href=\"/medellin/tour-guide/\">hire a private tour guide in Medellín</a>. For airport runs and day trips, see <a href=\"/medellin/private-driver/\">hire a private driver</a>. Planning a party? See <a href=\"/medellin/dj/\">hire a DJ</a> and <a href=\"/medellin/event-host/\">hire an event host</a>.</p>"),
         ]},
  "es": {"cat": "Qué hacer", "title": "Qué hacer en Medellín: atracciones y eventos | Blog de One World",
         "desc": "Las atracciones que la gente visita en Medellín (Comuna 13, Guatapé, Parque Arví, el centro) y cómo encontrar eventos, boletas y guías en un solo lugar.",
         "h1": "Qué hacer en Medellín: atracciones y eventos",
         "dek": "Lo que hacen primero los visitantes y los nuevos residentes, y dónde ver qué hay esta semana.",
         "sections": [
          ("Respuesta corta", "<p>Empiece con una caminata por el centro (Plaza Botero y el Museo de Antioquia), un recorrido por la Comuna 13, un viaje en Metrocable al Parque Arví y un día completo en Guatapé con El Peñón. Para salidas nocturnas, conciertos, networking y fiestas, use OneEvent para ver qué hay y comprar boletas. Revise horarios y precios en el sitio de cada atracción antes de ir.</p>"),
          ("Atracciones que la gente visita", "<ul><li><strong>Centro:</strong> Plaza Botero, el Museo de Antioquia y el Parque Berrío.</li><li><strong>Comuna 13:</strong> un barrio conocido por su arte urbano, las escaleras eléctricas al aire libre y su historia de cambio. Vaya con un guía local.</li><li><strong>Parque Arví:</strong> un parque natural al que se llega en Metrocable, sobre la ciudad.</li><li><strong>Pueblito Paisa y Cerro Nutibara:</strong> un mirador y una réplica de un pueblo tradicional.</li><li><strong>Parque Explora:</strong> un museo de ciencia con acuario.</li><li><strong>Guatapé y El Peñón:</strong> un viaje de día completo desde la ciudad, normalmente en carro privado o en tour.</li></ul>"),
          ("Eventos: qué hay esta semana", "<p>En <a href=\"" + ONEEVENT + "\">OneEvent</a> puede explorar eventos en Medellín, comprar boletas y hacer check-in con un código QR. Si organiza eventos, puede publicar el suyo y vender boletas en pesos o dólares.</p>"),
          ("Muévase y reserve ayuda", "<p>Para un día con un local, vea <a href=\"/es/medellin/tour-guide/\">contratar un guía turístico privado en Medellín</a>. Para traslados al aeropuerto y viajes de un día, vea <a href=\"/es/medellin/private-driver/\">contratar un conductor privado</a>. ¿Planea una fiesta? Vea <a href=\"/es/medellin/dj/\">contratar un DJ</a> y <a href=\"/es/medellin/event-host/\">contratar un animador</a>.</p>"),
         ]}},
 {"key": "furnished-rentals", "slug_en": "furnished-short-term-rentals-medellin", "slug_es": "arriendo-amoblado-corta-estadia-medellin", "img": "/assets/v2/img/apartment.jpg", "city": None, "app": ONEHOME, "new": True,
  "en": {"cat": "For renters", "title": "Furnished, monthly and short-term apartments in Medellín | One World",
         "desc": "How to search for a furnished, monthly or short-term apartment in Medellín: neighbourhoods, what to ask, what to check, and how to reach hosts directly on OneHome.",
         "h1": "Furnished, monthly and short-term apartments in Medellín: how to search",
         "dek": "Neighbourhoods, the questions to ask, and what to check before you send money.",
         "sections": [
          ("Short answer", "<p>For stays of a few days to a few months, look for furnished apartments (amoblados) in El Poblado, Laureles, Envigado or Sabaneta, ask exactly what the price includes, see the apartment before you pay, and get the terms in writing. A one-year lease is a different contract from a short stay, so ask which one the host is offering.</p>"),
          ("Where people look", "<ul><li><strong>El Poblado:</strong> the best-known area for visitors and expats, with restaurants and nightlife close by.</li><li><strong>Laureles:</strong> a flatter, more residential area that many people use for longer stays.</li><li><strong>Envigado and Sabaneta:</strong> quieter areas to the south, popular with people who want more space.</li></ul>"),
          ("Questions to ask the host", "<ul><li>What does the price include: building fees (administración), water, electricity, gas, internet, cleaning?</li><li>What is the minimum stay, and what is the price by the day, week and month?</li><li>Is the internet fast enough for video calls? Ask for a speed test.</li><li>What is the deposit, and when and how is it returned?</li><li>Who is the owner or authorised agent?</li></ul>"),
          ("Check before you pay", "<p>See the apartment in person or on a live video call, photograph the condition on day one, and never pay the full amount to someone you have not been able to identify. Our guides on <a href=\"/blog/is-renting-online-in-colombia-safe/\">spotting rental scams</a> and <a href=\"/blog/renting-in-medellin-guide/\">what to check before you rent</a> go through the details.</p>"),
          ("Find and message hosts", "<p>On <a href=\"" + ONEHOME + "\">OneHome</a> you can browse homes to rent or buy in Medellín and message the hosts and agents directly. If you own an apartment, you can post it too. Once you are settled, you can <a href=\"/medellin/cleaning/\">hire a cleaner by the day</a>.</p>"),
         ]},
  "es": {"cat": "Para arrendatarios", "title": "Apartamentos amoblados, por meses y por días en Medellín | Blog de One World",
         "desc": "Cómo buscar un apartamento amoblado, por meses o de corta estadía en Medellín: barrios, qué preguntar, qué revisar y cómo escribirles directamente a los anfitriones en OneHome.",
         "h1": "Apartamentos amoblados, por meses y de corta estadía en Medellín: cómo buscar",
         "dek": "Barrios, preguntas para el anfitrión y qué revisar antes de enviar dinero.",
         "sections": [
          ("Respuesta corta", "<p>Para estadías de unos días a unos meses, busque apartamentos amoblados en El Poblado, Laureles, Envigado o Sabaneta, pregunte exactamente qué incluye el precio, vea el apartamento antes de pagar y deje las condiciones por escrito. Un contrato de un año es distinto de una estadía corta, así que pregunte cuál ofrece el anfitrión.</p>"),
          ("Dónde buscan las personas", "<ul><li><strong>El Poblado:</strong> la zona más conocida por visitantes y extranjeros, con restaurantes y vida nocturna cerca.</li><li><strong>Laureles:</strong> una zona más plana y residencial que muchos usan para estadías largas.</li><li><strong>Envigado y Sabaneta:</strong> zonas más tranquilas al sur, populares entre quienes buscan más espacio.</li></ul>"),
          ("Preguntas para el anfitrión", "<ul><li>¿Qué incluye el precio: administración, agua, energía, gas, internet, aseo?</li><li>¿Cuál es la estadía mínima y cuánto cuesta por día, por semana y por mes?</li><li>¿El internet sirve para videollamadas? Pida una prueba de velocidad.</li><li>¿Cuál es el depósito y cuándo y cómo se devuelve?</li><li>¿Quién es el propietario o el agente autorizado?</li></ul>"),
          ("Revise antes de pagar", "<p>Vea el apartamento en persona o por videollamada en vivo, fotografíe el estado el primer día y no pague el valor completo a alguien que no ha podido identificar. Nuestras guías para <a href=\"/es/blog/es-seguro-arrendar-en-linea-colombia/\">detectar estafas al arrendar</a> y <a href=\"/es/blog/arrendar-en-medellin-guia/\">qué revisar antes de arrendar</a> explican los detalles.</p>"),
          ("Encuentre y escriba a los anfitriones", "<p>En <a href=\"" + ONEHOME + "\">OneHome</a> puede explorar viviendas para arrendar o comprar en Medellín y escribirles directamente a los anfitriones y agentes. Si usted tiene un apartamento, también puede publicarlo. Ya instalado, puede <a href=\"/es/medellin/cleaning/\">contratar una empleada por días</a>.</p>"),
         ]}},
 {"key": "buy-a-home", "slug_en": "buy-a-home-in-medellin-owner-financing", "slug_es": "comprar-casa-medellin-financiacion-del-vendedor", "img": "/assets/home.png", "city": "builder", "app": ONEHOME, "new": True,
  "en": {"cat": "For buyers", "title": "Buying a home in Medellín: for sale, owner financing, building | One World",
         "desc": "A plain guide to buying a house or apartment in Medellín: what to check, how owner financing works in general, and what to ask a lawyer.",
         "h1": "Buying a home in Medellín: houses for sale, owner financing and building",
         "dek": "What to check, what to ask the seller, and why a local lawyer belongs in the room.",
         "sections": [
          ("Short answer", "<p>Look at several homes, confirm who legally owns the one you want, agree the price and the payment terms in writing, and have a Colombian lawyer review the contract before you pay a deposit. Some sellers will accept payment in instalments (owner or seller financing); the terms vary, so everything about it needs to be written down and checked by a lawyer. This is general information, not legal advice.</p>"),
          ("Houses and apartments for sale", "<p>Used homes can be visited and compared; new apartments sold off plan are bought from a developer before they are finished, so check the developer's record and the delivery date in writing. On <a href=\"" + ONEHOME + "\">OneHome</a> you can browse homes for sale in Medellín and message the sellers and agents directly.</p>"),
          ("What to check before you pay", "<ul><li>Who owns the property, and whether it has any debts or claims on it. Ask a lawyer to review the ownership documents.</li><li>The condition of the building and any building-wide charges (administración).</li><li>That the person you are dealing with is the owner or an authorised agent.</li><li>The exact price, the currency, what is included, and the date of the deed signing.</li></ul>"),
          ("Owner (seller) financing: what to ask", "<ul><li>How much do you pay up front, and how much in instalments?</li><li>What is the interest rate, if any, and what is the payment schedule?</li><li>What guarantees the seller has, and what happens if you miss a payment?</li><li>When do you receive the deed, and how is the debt recorded?</li></ul><p>Do not sign or transfer money until a lawyer has read the agreement and explained these points to you.</p>"),
          ("Building on your own lot", "<p>If you plan to build, you will need plans, a professional such as an architect or engineer, a building permit and a crew. For labour prices and what to put in the contract, see <a href=\"/medellin/builder/\">hire a builder or contractor in Medellín</a>.</p>"),
         ]},
  "es": {"cat": "Para compradores", "title": "Comprar casa en Medellín: en venta, financiación del vendedor | One World",
         "desc": "Guía sencilla para comprar casa o apartamento en Medellín: qué revisar, cómo funciona la financiación directa del vendedor y qué consultar con un abogado.",
         "h1": "Comprar casa en Medellín: casas en venta, financiación del vendedor y construcción",
         "dek": "Qué revisar, qué preguntar al vendedor y por qué un abogado local debe estar presente.",
         "sections": [
          ("Respuesta corta", "<p>Visite varias casas, confirme quién es el propietario legal de la que quiere, acuerde por escrito el precio y las condiciones de pago, y pida a un abogado colombiano que revise el contrato antes de pagar cualquier anticipo. Algunos vendedores aceptan pagos en cuotas (financiación directa del vendedor); las condiciones varían, así que todo debe quedar por escrito y revisado por un abogado. Es información general, no asesoría legal.</p>"),
          ("Casas y apartamentos en venta", "<p>Las viviendas usadas se pueden visitar y comparar; los apartamentos nuevos sobre planos se compran a una constructora antes de estar terminados, así que revise el historial de la constructora y la fecha de entrega por escrito. En <a href=\"" + ONEHOME + "\">OneHome</a> puede explorar viviendas en venta en Medellín y escribirles directamente a los vendedores y agentes.</p>"),
          ("Qué revisar antes de pagar", "<ul><li>Quién es el propietario y si el inmueble tiene deudas o gravámenes. Pida a un abogado que revise los documentos de propiedad.</li><li>El estado del edificio y las cuotas de administración.</li><li>Que la persona con quien trata sea el propietario o un agente autorizado.</li><li>El precio exacto, la moneda, lo que incluye y la fecha de firma de la escritura.</li></ul>"),
          ("Financiación del vendedor: qué preguntar", "<ul><li>¿Cuánto paga de entrada y cuánto en cuotas?</li><li>¿Cuál es la tasa de interés, si la hay, y el calendario de pagos?</li><li>¿Qué garantías tiene el vendedor y qué pasa si usted deja de pagar una cuota?</li><li>¿Cuándo recibe la escritura y cómo se registra la deuda?</li></ul><p>No firme ni transfiera dinero hasta que un abogado haya leído el acuerdo y le haya explicado estos puntos.</p>"),
          ("Construir en su propio lote", "<p>Si piensa construir, necesitará planos, un profesional como arquitecto o ingeniero, licencia de construcción y una cuadrilla. Para precios de mano de obra y qué poner en el contrato, vea <a href=\"/es/medellin/builder/\">contratar un maestro de obra o constructor en Medellín</a>.</p>"),
         ]}},
]
