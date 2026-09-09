(function () {
  'use strict';
  if (!window.OV_DICT) return;

  function copy(us, es, de, ru, cn, br) {
    return { us: us, es: es, co: es, de: de, ru: ru, cn: cn, br: br };
  }

  var guarantee = copy(
    '30-day money-back guarantee. Setup fee included.',
    'Garantía de devolución de 30 días. Incluye la instalación.',
    '30-Tage-Geld-zurück-Garantie. Einrichtung inbegriffen.',
    '30-дневная гарантия возврата. Настройка включена.',
    '30 天退款保证，包含设置费。',
    'Garantia de reembolso de 30 dias. Configuração incluída.'
  );
  var getStarted = copy('Get started', 'Comenzar', 'Loslegen', 'Начать', '开始', 'Começar');
  var getStartedArrow = copy('Get started &rarr;', 'Comenzar &rarr;', 'Loslegen &rarr;', 'Начать &rarr;', '开始 &rarr;', 'Começar &rarr;');
  var getStartedInstead = copy('Get started instead', 'Comenzar en su lugar', 'Stattdessen loslegen', 'Вместо этого начать', '改为开始', 'Começar em vez disso');
  var guaranteeQuestion = copy(
    'How does the 30-day money-back guarantee work?',
    '¿Cómo funciona la garantía de devolución de 30 días?',
    'Wie funktioniert die 30-Tage-Geld-zurück-Garantie?',
    'Как работает 30-дневная гарантия возврата?',
    '30 天退款保证如何运作？',
    'Como funciona a garantia de reembolso de 30 dias?'
  );
  var guaranteeAnswer = copy(
    'Setup and your first month are charged on day one. If OneVoice is not right for you, cancel within 30 days and we refund your setup fee and your plan fee in full. Minutes used beyond your plan allowance are not refunded.',
    'La instalación y el primer mes se cobran el primer día. Si OneVoice no es para ti, cancela dentro de 30 días y devolvemos íntegros la instalación y el plan. Los minutos de exceso no se reembolsan.',
    'Einrichtung und erster Monat werden am ersten Tag berechnet. Wenn OneVoice nicht passt, kündigen Sie innerhalb von 30 Tagen; wir erstatten Einrichtung und Tarif vollständig. Mehrminuten werden nicht erstattet.',
    'Настройка и первый месяц оплачиваются в первый день. Если OneVoice вам не подходит, отмените в течение 30 дней — мы полностью вернём плату за настройку и план. Сверхлимитные минуты не возвращаются.',
    '设置费和首月费用在第一天收取。如果 OneVoice 不适合您，请在 30 天内取消，我们将全额退还设置费和套餐费。超额分钟不退款。',
    'A configuração e o primeiro mês são cobrados no primeiro dia. Se o OneVoice não servir para você, cancele em até 30 dias e reembolsamos integralmente a configuração e o plano. Minutos excedentes não são reembolsados.'
  );
  var pricingSummary = copy(
    'Answer is $149/mo with 200 talk minutes. Front Desk is $297/mo with 500 minutes. Custom is quoted above 500 minutes, with a $449 monthly minimum. Setup is $299.',
    'Answer cuesta $149/mes con 200 minutos. Front Desk cuesta $297/mes con 500 minutos. Custom se cotiza por encima de 500 minutos, con un mínimo de $449/mes. La instalación cuesta $299.',
    'Answer kostet $149/Monat mit 200 Minuten. Front Desk kostet $297/Monat mit 500 Minuten. Custom wird über 500 Minuten angeboten, mindestens $449/Monat. Einrichtung: $299.',
    'Answer — $149/мес. и 200 минут. Front Desk — $297/мес. и 500 минут. Custom рассчитывается свыше 500 минут, минимум $449/мес. Настройка — $299.',
    'Answer 每月 $149，含 200 分钟；Front Desk 每月 $297，含 500 分钟；超过 500 分钟的 Custom 方案单独报价，每月最低 $449。设置费 $299。',
    'Answer custa $149/mês com 200 minutos. Front Desk custa $297/mês com 500 minutos. Custom é cotado acima de 500 minutos, com mínimo de $449/mês. Configuração: $299.'
  );

  var overrides = {
    ka1db3a8070: getStarted,
    k0bcf2784ed: getStartedArrow,
    k6164fa1609: getStartedInstead,
    k723baf9b2f: guarantee,
    k147bcd15ed: guarantee,
    k707ce655fa: copy(', with a 30-day money-back guarantee', ', con garantía de devolución de 30 días', ', mit 30-Tage-Geld-zurück-Garantie', ', с 30-дневной гарантией возврата', '，并享有 30 天退款保证', ', com garantia de reembolso de 30 dias'),
    k98bdb96720: guaranteeQuestion,
    k36c6fb36bc: guaranteeQuestion,
    k3ae4452141: guaranteeAnswer,
    k6717758279: guaranteeAnswer,
    k4d94eb09f4: guarantee,
    k86516c84fd: copy('Pricing, guarantee, integrations, cancelling', 'Precios, garantía, integraciones y cancelación', 'Preise, Garantie, Integrationen und Kündigung', 'Цены, гарантия, интеграции и отмена', '价格、保证、集成与取消', 'Preços, garantia, integrações e cancelamento'),
    ke59488952c: copy('Small teams sign up online and are live in minutes. Setup and the first month are charged on day one, with a 30-day money-back guarantee.', 'Los equipos pequeños se registran en línea y empiezan en minutos. La instalación y el primer mes se cobran el primer día, con garantía de devolución de 30 días.', 'Kleine Teams melden sich online an und sind in Minuten startklar. Einrichtung und erster Monat werden am ersten Tag berechnet, mit 30-Tage-Garantie.', 'Небольшие команды регистрируются онлайн и запускаются за минуты. Настройка и первый месяц оплачиваются в первый день, с 30-дневной гарантией.', '小团队可在线注册并快速启用。设置费和首月费用在第一天收取，并享有 30 天退款保证。', 'Equipes pequenas assinam online e entram no ar em minutos. Configuração e primeiro mês são cobrados no primeiro dia, com garantia de 30 dias.'),
    ke8fea28ece: copy('Building your agent costs a flat $299. It is charged on day one with the first plan period and is covered by the 30-day money-back guarantee.', 'Crear tu agente cuesta $299. Se cobra el primer día junto con el primer periodo del plan y está cubierto por la garantía de 30 días.', 'Der Aufbau kostet pauschal $299, wird am ersten Tag mit dem ersten Tarifzeitraum berechnet und fällt unter die 30-Tage-Garantie.', 'Создание агента стоит $299, оплачивается в первый день вместе с первым периодом плана и покрывается 30-дневной гарантией.', '创建客服的固定设置费为 $299，与首个套餐周期在第一天收取，并受 30 天退款保证保护。', 'A criação do agente custa $299, cobrada no primeiro dia com o primeiro período do plano e coberta pela garantia de 30 dias.'),
    k002205d97c: copy('Annual billing saves 35% on Front Desk. Answer is billed monthly at $149.', 'La facturación anual ahorra 35% en Front Desk. Answer se factura mensualmente a $149.', 'Jahresabrechnung spart 35% bei Front Desk. Answer kostet monatlich $149.', 'Годовая оплата экономит 35% на Front Desk. Answer оплачивается ежемесячно по $149.', 'Front Desk 年付可省 35%。Answer 按月收取 $149。', 'A cobrança anual economiza 35% no Front Desk. Answer custa $149 por mês.'),
    k9d81868002: pricingSummary,
    k1643c8aa36: pricingSummary,
    k4306105b3b: copy('You buy talk minutes, not seats. Answer covers 200 minutes, Front Desk covers 500, and Custom is quoted for higher volume, multiple locations, or connected systems.', 'Compras minutos, no puestos. Answer cubre 200 minutos, Front Desk 500 y Custom se cotiza para mayor volumen, varias ubicaciones o sistemas conectados.', 'Sie kaufen Minuten, keine Plätze. Answer enthält 200 Minuten, Front Desk 500; Custom wird für höheres Volumen, mehrere Standorte oder Anbindungen angeboten.', 'Вы покупаете минуты, а не места. Answer включает 200 минут, Front Desk — 500; Custom рассчитывается для большего объёма, нескольких точек или интеграций.', '您购买的是通话分钟而非坐席。Answer 含 200 分钟，Front Desk 含 500 分钟；更高话务量、多地点或系统集成使用 Custom 报价。', 'Você compra minutos, não assentos. Answer cobre 200 minutos, Front Desk 500 e Custom é cotado para maior volume, várias unidades ou integrações.'),
    k1c10d1680b: copy('. Sized for higher volume.', '. Preparado para mayor volumen.', '. Für höheres Volumen ausgelegt.', '. Масштабируется под больший объём.', '，也能满足更高话务量。', '. Dimensionado para maior volume.'),
    k438226dccf: copy('Answer', 'Answer', 'Answer', 'Answer', 'Answer', 'Answer'),
    kd6663dda5f: copy('Front Desk', 'Front Desk', 'Front Desk', 'Front Desk', 'Front Desk', 'Front Desk'),
    k66d0c5e6b1: copy('Custom', 'Custom', 'Custom', 'Custom', 'Custom', 'Custom'),
    k95a5c35e02: copy('One local number, 200 minutes, and 24/7 answering.', 'Un número local, 200 minutos y atención 24/7.', 'Eine lokale Nummer, 200 Minuten und Erreichbarkeit rund um die Uhr.', 'Один местный номер, 200 минут и ответы 24/7.', '一个本地号码、200 分钟和全天候接听。', 'Um número local, 200 minutos e atendimento 24/7.'),
    kc600c5716f: copy('One number, 500 minutes, and a lower overage rate.', 'Un número, 500 minutos y una tarifa de exceso menor.', 'Eine Nummer, 500 Minuten und ein günstigerer Mehrminutenpreis.', 'Один номер, 500 минут и более низкая цена сверх лимита.', '一个号码、500 分钟和更低的超额费率。', 'Um número, 500 minutos e menor tarifa excedente.'),
    k497335ef00: copy('Quoted for more than 500 minutes, multiple locations, or connected systems.', 'Cotizado para más de 500 minutos, varias ubicaciones o sistemas conectados.', 'Individuelles Angebot für mehr als 500 Minuten, mehrere Standorte oder angebundene Systeme.', 'Индивидуальная цена свыше 500 минут, для нескольких точек или интеграций.', '超过 500 分钟、多地点或系统集成时单独报价。', 'Cotado para mais de 500 minutos, várias unidades ou sistemas conectados.'),
    kcf5a311790: copy('Everything in Answer', 'Todo lo de Answer', 'Alles aus Answer', 'Всё из Answer', '包含 Answer 的全部功能', 'Tudo do Answer'),
    kb7da1b9c50: copy('Quoted above 500 minutes · $449/mo minimum', 'Cotizado por encima de 500 minutos · mínimo $449/mes', 'Angebot über 500 Minuten · mindestens $449/Monat', 'Цена свыше 500 минут · минимум $449/мес.', '超过 500 分钟单独报价 · 每月最低 $449', 'Cotado acima de 500 minutos · mínimo de $449/mês'),
    k58e4e2d291: copy('Custom talk-minute allowance', 'Volumen de minutos Custom', 'Individuelles Minutenvolumen', 'Индивидуальный объём минут', 'Custom 通话分钟额度', 'Franquia de minutos Custom'),
    k6f840defc8: copy('When do I need Custom?', '¿Cuándo necesito Custom?', 'Wann brauche ich Custom?', 'Когда нужен Custom?', '什么时候需要 Custom？', 'Quando preciso do Custom?'),
    kd4b3ce9604: copy('Choose Custom when you need more than 500 minutes, multiple locations, or a connection to your system of record. It is quoted for your use case and never below $449 per month.', 'Elige Custom cuando necesites más de 500 minutos, varias ubicaciones o conexión con tu sistema principal. Se cotiza según tu caso y nunca por debajo de $449 al mes.', 'Wählen Sie Custom bei mehr als 500 Minuten, mehreren Standorten oder einer Anbindung an Ihr Kernsystem. Das Angebot liegt nie unter $449 pro Monat.', 'Выбирайте Custom, если нужно больше 500 минут, несколько точек или интеграция с основной системой. Цена рассчитывается индивидуально и не бывает ниже $449 в месяц.', '需要超过 500 分钟、多地点或连接业务主系统时，请选择 Custom。方案按需求报价，每月不低于 $449。', 'Escolha Custom para mais de 500 minutos, várias unidades ou integração com seu sistema principal. O preço é cotado e nunca fica abaixo de $449/mês.'),
    kd399bfb0be: copy('How many minutes do I need?', '¿Cuántos minutos necesito?', 'Wie viele Minuten brauche ich?', 'Сколько минут мне нужно?', '我需要多少分钟？', 'De quantos minutos preciso?'),
    k755e282fce: copy('Answer includes 200 minutes and Front Desk includes 500. If you expect more than 500, we quote Custom around your call volume.', 'Answer incluye 200 minutos y Front Desk 500. Si esperas más de 500, cotizamos Custom según tu volumen.', 'Answer enthält 200 Minuten, Front Desk 500. Für mehr als 500 erstellen wir ein Custom-Angebot passend zum Volumen.', 'Answer включает 200 минут, Front Desk — 500. Если ожидается больше 500, мы рассчитаем Custom под ваш объём.', 'Answer 包含 200 分钟，Front Desk 包含 500 分钟。预计超过 500 分钟时，我们会按通话量报价 Custom。', 'Answer inclui 200 minutos e Front Desk 500. Acima de 500, cotamos Custom conforme o volume.'),
    k9277aca233: copy('Can I cancel?', '¿Puedo cancelar?', 'Kann ich kündigen?', 'Можно отменить?', '可以取消吗？', 'Posso cancelar?'),
    k75917d36de: copy('Answer and Front Desk are month-to-month. Cancel within 30 days for a refund of setup and plan fees; minutes beyond your plan allowance are not refunded. Custom terms are stated in your quote.', 'Answer y Front Desk son mensuales. Cancela dentro de 30 días para recuperar instalación y plan; los minutos excedentes no se reembolsan. Los términos de Custom figuran en tu cotización.', 'Answer und Front Desk sind monatlich kündbar. Bei Kündigung binnen 30 Tagen werden Einrichtung und Tarif erstattet; Mehrminuten nicht. Custom-Bedingungen stehen im Angebot.', 'Answer и Front Desk оплачиваются помесячно. При отмене в течение 30 дней возвращаются настройка и план; сверхлимитные минуты не возвращаются. Условия Custom указаны в предложении.', 'Answer 和 Front Desk 按月订购。30 天内取消可退还设置费和套餐费；超额分钟不退款。Custom 条款以报价为准。', 'Answer e Front Desk são mensais. Cancele em 30 dias para reembolso da configuração e do plano; minutos excedentes não são reembolsados. Os termos do Custom constam na proposta.'),
    k758068970a: copy('Answer is $149/mo with 200 talk minutes included. One booked job can cover it several times over.', 'Answer cuesta $149/mes e incluye 200 minutos. Un solo trabajo reservado puede pagarlo varias veces.', 'Answer kostet $149/Monat inklusive 200 Minuten. Ein gebuchter Auftrag kann das mehrfach decken.', 'Answer стоит $149/мес. и включает 200 минут. Один заказ может окупить его несколько раз.', 'Answer 每月 $149，含 200 分钟。一笔预约业务往往就能覆盖数倍成本。', 'Answer custa $149/mês com 200 minutos. Um serviço agendado pode pagar o plano várias vezes.'),
    k923c1f9223: pricingSummary,
    k9a487603df: guaranteeAnswer
  };

  Object.keys(overrides).forEach(function (key) {
    window.OV_DICT[key] = overrides[key];
  });
})();
