---
type: Market Fact
title: "Средний retention мобильных приложений: 25,4% iOS / 20,2% Android на день 1, падает до 5,3% iOS / 3,8% Android к дню 30 (данные AppsFlyer, вторичная компиляция)"
description: Ориентир отраслевого стандарта удержания для нового сервисного приложения — что считается нормой на день 1 и день 30 по агрегированным данным AppsFlyer.
resource: https://www.businessofapps.com/data/app-retention-rates/
tags: [analytics, retention, cohort, mobile-app, robotaxi, measurement, international]
status: stable
generated: { by: researcher, at: 2026-07-31T15:53:47+03:00 }
verified: { by: null, at: null }
stale_after: 2027-07-31
sources:
  - id: businessofapps-retention-2026-07-31
    resource: https://www.businessofapps.com/data/app-retention-rates/
    title: "Business of Apps: App Retention Rates (2026)"
    last_modified: 2026-07-31
    snapshot: knowledge/references/2026-07-31_businessofapps-com_app-retention-rates-2026.md
    confidence: PLAUSIBLE
---

Отраслевой ориентир retention (доли пользователей, вернувшихся в приложение) по агрегированным данным мобильного трекингового вендора AppsFlyer, пересказанный в обзоре Business of Apps.[^businessofapps-retention-2026-07-31]

> «The average iOS app retention rate was 25.4% on day one, dropping to 5.3% by day 30 (AppsFlyer). The average Android app retention rate was lower, at 20.2% on day one and 3.8% by day 30.»

Тот же обзор фиксирует общий порядок величины оттока для рынка приложений в целом:

> «However, app retention rates across the board are low, with more than 90 percent of users giving up on an app before the 30 day mark.»

Обзор также ранжирует категории приложений: новостные/журнальные приложения показывают одни из самых высоких retention, генеративный ИИ и фото/видео — одни из самых низких; данных отдельно по такси/mobility-сервисам на открытой (бесплатной) части страницы нет — детальные таблицы по категориям и странам закрыты регистрацией.

## Что из этого следует для пилота

Цифры общие по всему рынку приложений, не по такси/mobility-вертикали — использовать как грубый ориентир порядка величины (день 1 около 20-25%, день 30 около 4-5%), а не как целевой KPI пилота. День 60 и день 90 — метрики, которые прямо запрошены методикой пилота — на этой странице не встречаются вовсе.

## Расхождения

Не расхождение, а ограничение источника: Business of Apps не публикует собственную методологию сбора, а пересказывает цифру от AppsFlyer (ссылка на https://www.appsflyer.com/benchmarks/, которая не скрейпилась в рамках этой задачи). Это вторичная компиляция вторичного отчёта — отсюда статус `PLAUSIBLE`, а не `CONFIRMED`.

## Дыры

- День 60 и день 90 retention — не найдены ни на этой странице, ни в целевом поиске в рамках бюджета задачи.
- Отраслевые методические материалы российских объединений (например, профильных ассоциаций мобильного маркетинга) по когортному анализу retention — не искались отдельно, бюджет запросов исчерпан на общий поиск.
- Бенчмарк по вертикали «такси/мобильность» отдельно не найден; общий ответ рынка приложений применён без поправки на специфику сервиса разовых поездок.
- Первоисточник AppsFlyer (appsflyer.com/benchmarks) не прочитан напрямую — карточка полагается на пересказ Business of Apps.

---
Входит в хаб [[методики-замера]]. Конвенции базы — [[СХЕМА]].

Снимок источника: [[2026-07-31_businessofapps-com_app-retention-rates-2026]]
