---
type: Market Fact
title: "Google Ads Conversion Lift по географии — официальная методика гео-инкрементальности (тест/контроль регионы, iROAS), в российских системах прямого аналога не найдено"
description: Международный эталон гео-эксперимента для сравнения тестовой и контрольной территории; фиксирует, что перенос в Яндекс Директ/Рекламу не автоматический.
resource: https://support.google.com/google-ads/answer/14102986
tags: [analytics, ads, channels, measurement, international, robotaxi]
status: stable
generated: { by: researcher, at: 2026-07-31T15:53:47+03:00 }
verified: { by: null, at: null }
stale_after: 2027-01-27
sources:
  - id: google-ads-geo-lift-2026-07-31
    resource: https://support.google.com/google-ads/answer/14102986
    title: "Google Ads Help: Understand your Conversion Lift based on geography measurement data"
    last_modified: 2026-07-31
    snapshot: knowledge/references/2026-07-31_support-google-com_conversion-lift-geography.md
    confidence: CONFIRMED
---

Google Ads официально предлагает продукт «Conversion Lift based on geography» — измерение причинного, инкрементального эффекта кампании через сравнение неперекрывающихся географических регионов (тестовых и контрольных).[^google-ads-geo-lift-2026-07-31]

> «Conversion Lift based on geography measures the causal, incremental impact of your campaigns by aggregating unattributed conversions into non-overlapping geographic regions and isolation differences between baseline and exposed. Conversion Lift based on geography typically requires a higher budget than the user-based alternative.»

Ключевая метрика — iROAS (Incremental Return on Ad Spend): инкрементальная ценность конверсий, делённая на инкрементальные затраты, с доверительным интервалом.

> «Incremental conversion value/Incremental Cost = iROAS... if your study results in getting an iROAS of 2, that means that for every $1 USD invested, your business generated $2 USD net new in conversion value that otherwise wouldn't have existed.»

Методология опирается на опубликованные исследования Google: «Trimmed Match Design for Randomized Paired Geo Experiments», «Estimating Ad Effectiveness using Geo Experiments in a Time-Based Regression Framework» и «A Time-Based Regression Matched Markets Approach for Designing Geo Experiments (TBR+MM)» — статистические методы подбора пар «тестовый регион — контрольный регион» и оценки эффекта.

Инструмент даёт три статуса результата: «Significant Positive iROAS» (значимый положительный эффект), «Not enough data» (не хватило данных/бюджета) и «No significant lift detected» (эффект статистически не обнаружен).

## Перенос на российский контур — не автоматический

Это продукт Google Ads, требующий доступа к рекламному кабинету и статистике конкретной платформы; методика (парные гео, регрессия по времени) переносима на бумаге, но требует отдельной инженерной реализации, если внутри Яндекс Директа/Рекламы аналогичного встроенного инструмента нет (см. карточку `direkt-ab-eksperimenty-net-geo-test-kontrol`). Прямого использования продукта Google в РФ для пилота роботакси не подразумевается — карточка фиксирует только методику как ориентир.

## Дыры

Аналогичная официальная страница Meta (Conversion Lift / geo lift study) не проверялась — не входила в бюджет запросов задачи.

---
Входит в хаб [[методики-замера]]. Конвенции базы — [[СХЕМА]].

Снимок источника: [[2026-07-31_support-google-com_conversion-lift-geography]]
