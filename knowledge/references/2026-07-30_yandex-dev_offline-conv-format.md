Шаг 1\. Подготовка данных

# Передача офлайн-конверсий

О том, что такое офлайн-конверсии и какие бизнес-задачи можно решить, отслеживая их, см. в разделе [Офлайн-конверсии и звонки](https://yandex.ru/dev/metrika/ru/management/conversion).

## Шаг 1\. Подготовка данных

1. Подготовьте [специальные идентификаторы](https://yandex.ru/dev/metrika/ru/management/conversion#cpec-ids) — `ClientID`, `UserID`, `yclid` или `PurchaseId`.

Примечание

Хотя бы один из этих идентификаторов обязателен для передачи. Без него конверсия не будет привязана к визиту.

2. Создайте цель [JavaScript-событие](https://yandex.ru/support/metrica/general/goal-js-event.html) с помощью метода [POST /management/v1/counter/{counterId}/goals](https://yandex.ru/dev/metrika/ru/management/openapi/goal/addGoal). В качестве идентификатора цели укажите событие, которое нужно отслеживать (например, подтверждение заказа — «order\_confirmed»). Этот идентификатор понадобится при формировании CSV-файла.

Примечание

При создании цели «JavaScript-событие» обязательно используйте условие «совпадает».

Можно использовать ранее созданную цель, если конверсия по этой цели совершается и на сайте, и вне его и вы хотите получать общую статистику.

## Шаг 2\. Подготовка данных о конверсиях

Данные о конверсиях передаются в CSV-формате. Вы можете передать их несколькими способами:

CSV-файл (рекомендуемый)

multipart/form-data

В файле укажите данные, которые хотите передать в Метрику. [Пример файла](https://download.cdn.yandex.net/from/yandex.ru/support/ru/metrica/files/offline-conversions.csv).

В первой строке необходимо передать названия колонок.

|     |     |
| --- | --- |
| **Колонки** | **Описание** |
| **Обязательные** |  |
| `Target` | Идентификатор цели. |
| `DateTime` | Дата и время конверсии в формате [Unix Time Stamp](http://www.unixtimestamp.com/index.php).<br>В DateTime можно указывать только прошедшее время. Если на момент загрузки файла время из DateTime еще не наступило, возникнет ошибка. |
| **Обязательные для привязки к визиту** — укажите хотя бы один из этих идентификаторов. |  |
| `UserId` | Идентификатор посетителя сайта, назначенный владельцем сайта. |
| `ClientId` | Идентификатор посетителя сайта, назначенный Яндекс Метрикой. |
| `Yclid` | Идентификатор клика по рекламному объявлению Яндекс Директа, назначается Яндекс.Директом. Передается в URL объявления. |
| `PurchaseId` | Идентификатор покупки электронной коммерции назначенный владельцем сайта. |
| **Необязательные** |  |
| `Price` | Цена (ценность) цели, десятичным разделителем является точка (.). |
| `Currency` | Валюта в трехбуквенном формате ISO 4217. |

## Шаг 3\. Передача данных

Примечание

Сформируйте CSV-файл с информацией и передайте его с помощью данного метода. Также рекомендуем генерировать запросы к API в автоматическом режиме с помощью модулей языка программирования.

Примечание

Данные появятся в отчетах Метрики в течение двух часов после их загрузки.

C помощью метода [POST /management/v1/counter/{counterId}/offline\_conversions/upload](https://yandex.ru/dev/metrika/ru/management/openapi/offline_conversions/upload_1). Укажите во входных данных OAuth-токен и номер счетчика.

PHP

Python

```
$counter = "";            // Specify the counter ID
$token = "";              // Specify the OAuth token

$curl = curl_init("https://api-metrika.yandex.net/management/v1/counter/$counter/offline_conversions/upload");

curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, array('file' => new CurlFile(realpath('file.csv'))));
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_HTTPHEADER, array("Content-Type: multipart/form-data", "Authorization: OAuth $token"));

$result = curl_exec($curl);

echo $result;

curl_close($curl);
```

```
import requests

counter = 123456
token = "token"

file = open("offline-conversions.csv", "r").read()

url = "https://api-metrika.yandex.net/management/v1/counter/{}/offline_conversions/upload".format(counter)
headers = {
 "Authorization": "OAuth {}".format(token)
}

req = requests.post(url, headers=headers, files={"file":file})
```

## Что делать дальше?

Отслеживайте статус загрузки конверсий с помощью метода [GET /management/v1/counter/{counterId}/offline\_conversions/uploading/{id}](https://yandex.ru/dev/metrika/ru/management/openapi/offline_conversions/findById_1).

## Узнайте больше

### Была ли статья полезна?

ДаНет

Предыдущая

Следующая

---
Снимок нормализован: убраны навигация и пустые блоки. Полный оригинал: `knowledge/references/_полные/2026-07-30_yandex-dev_offline-conv-format.md.gz`
