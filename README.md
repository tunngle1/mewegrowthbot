# MeWeGo Bot V2

Telegram бот для приёма заявок с сайта MeWeGo Growth, созданный с нуля для Vercel.

## Установка на Vercel

1. Создайте новый проект на Vercel
2. Подключите GitHub репозиторий
3. Добавьте переменную окружения:
   - Key: `BOT_TOKEN`
   - Value: `8845154408:AAHp-8XOHEayxdtFX9XovyDFo8Ox53j4naI`
4. Deploy

## API Endpoints

- `/api/test` — проверка работы
- `/api/lead` — приём заявок с формы
- `/api/xray` — приём результатов Business X-Ray

## Настройка бота

1. Добавьте бота в нужный чат Telegram
2. Напишите `/start` боту
3. Бот сохранит chat_id и будет отправлять туда заявки