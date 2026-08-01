---
type: Market Fact
title: "Офлайн-конверсии в Метрику: CSV с Target и DateTime, привязка по yclid, окно дополнения визитов 21 день"
description: Технические требования к загрузке офлайн-конверсий — механика, которая превращает замер из «стоимости заявки» в «стоимость первой поездки».
resource: https://yandex.ru/dev/metrika/ru/management/offline-conv
tags: [analytics, ads, channels, russia]
status: stable
generated: { by: researcher, at: 2026-07-30T17:18:12+03:00 }
verified: { by: null, at: null }
stale_after: 2027-01-26
sources:
  - id: yandex-offline-conv-2026-07-30
    resource: https://yandex.ru/dev/metrika/ru/management/offline-conv
    title: Яндекс Метрика. Передача офлайн-конверсий
    last_modified: 2026-07-30
    snapshot: knowledge/references/2026-07-30_yandex-dev_offline-conv-format.md
    confidence: CONFIRMED
  - id: yandex-offline-params-2026-07-30
    resource: https://yandex.ru/support/metrica/ru/data/offline-params
    title: Яндекс Метрика. Импорт офлайн-данных
    last_modified: 2026-07-30
    snapshot: knowledge/references/2026-07-30_yandex-support_offline-params.md
    confidence: CONFIRMED
---

Формат файла: CSV, UTF-8, первая строка — названия колонок, регистр важен.[^yandex-offline-conv-2026-07-30]

Обязательные колонки — `Target` (идентификатор цели) и `DateTime` (Unix timestamp, только прошедшее время). Привязка — хотя бы одна из `UserId`, `ClientId`, `Yclid`, `PurchaseId`. Опционально `Price` (разделитель — точка) и `Currency` (ISO 4217).

`Yclid` — идентификатор клика по объявлению Директа, приходит в URL объявления и сохраняется на сайте скриптом в cookie, дальше подставляется в скрытое поле формы.

**Ограничение, которое определяет всю схему замера:**

> «Для всех офлайн-данных (офлайн-конверсий, звонков, заказов из CRM) период дополнения визитов составляет 21 день. Данные будут добавлены к визиту, если между последним визитом посетителя на сайт и моментом обработки файла с данными о конверсиях прошло не больше 21 дня.»[^yandex-offline-params-2026-07-30]

Обработка занимает до двух часов, размер файла — до 1 ГБ. API: `POST https://api-metrika.yandex.net/management/v1/counter/{counterId}/offline_conversions/upload`, `multipart/form-data`, поле `file`, параметр `type` — `BASIC`, `CALLS` или `CHATS`. Для звонков отдельный эндпоинт `upload_calls`.

## Что из этого следует для замера

Окно в 21 день задаёт горизонт атрибуции. Для сервиса такси это значит: первая поездка, случившаяся позже трёх недель после клика, к рекламному источнику уже не привяжется — и это надо закладывать в план, а не обнаруживать в отчёте.

Схема целиком: метка и `yclid` в ссылке → сохранение в cookie и скрытое поле → событие или CRM → выгрузка оплативших → загрузка обратно в Метрику. Без последнего шага платформа считает ценность конверсии по своей догадке, а не по факту.

## Дыры

Справка не даёт отдельного лимита на то, насколько давним может быть `DateTime` — сказано только «прошедшее время». Практический предел задаёт окно в 21 день.

---
Входит в хаб [[требования-площадок]]. Конвенции базы — [[СХЕМА]].

Снимок источника: [[2026-07-30_yandex-dev_offline-conv-format]], [[2026-07-30_yandex-support_offline-params]]
