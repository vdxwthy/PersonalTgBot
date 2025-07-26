# DevVdxwthyBot 🤖

Просто личный ТГ-ботик

## 📋 Описание

Бот автоматически отправляет и обновляет сообщение в Telegram-канале с текущим временем, датой и прогрессом дня/года в виде JavaScript объекта. Поддерживает гибкую настройку отображаемых полей и часовых поясов.

### Пример вывода:
```javascript
const life = {
  day: 15,
  month: 12,
  year: 2024,
  hour: 14,
  minute: 30,
  seconds: 45,
  dayOfWeek: 'Sunday',
  dayProgress: 60.42%,
  yearProgress: 95.123456%,
}
```


## 🥱 Установка

### Требования
- Python 3.10+
- Poetry

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/vdxwthy/DevVdxwthyBot.git
cd DevVdxwthyBot
```

2. Установите зависимости:
```bash
poetry install
```

3. Создайте файл `.env` и добавьте ваши токены:
```env
BOT_TOKEN=your_telegram_bot_token
CHANNEL_ID=your_channel_id
```

## ⚙️ Настройка

### Конфигурационный файл `settings.conf`

#### Секция `[Features]`
- `year`, `month`, `days`, `hours`, `minutes`, `seconds` - отображение соответствующих полей времени/даты
- `day_of_week` - отображение дня недели
- `day_progress` - прогресс текущего дня в процентах
- `year_progress` - прогресс текущего года в процентах
- `update_interval` - интервал обновления в секундах (рекомендуется не менее 5)
- `timezone_offset` - смещение от UTC в часах (может быть отрицательным)

#### Секция `[Order]`
- `fields` - порядок отображения полей в сообщении

#### Секция `[Telegram]`
- `message_id` - автоматически сохраняется ID сообщения для редактирования

### Примеры настройки часовых поясов
- `timezone_offset = 0` - UTC
- `timezone_offset = 3` - MSK (Москва)
- `timezone_offset = 5` - Екатеринбург
- `timezone_offset = -5` - EST (Восточное время США)
