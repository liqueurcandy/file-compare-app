# File Compare App

Веб-приложение для сравнения текстовых файлов и Word-файлов (.docx).

## Технологии
- **Backend**: Python, FastAPI
- **Frontend**: Vue.js 3, Vite
- **Для Word-файлов**: python-docx

## Установка и запуск

### 1. Установка зависимостей

**Backend (Python):**
```bash
pip install fastapi uvicorn python-multipart chardet python-docx
```

**Frontend (Vue):**
```bash
cd frontend
npm install
```


### 2. Запуск

**Backend:**
```bash
python main.py
```
Сервер запустится на http://localhost:8000


**Frontend:**
```bash
cd frontend
npm run dev
```
Приложение откроется на http://localhost:5173


### 3. Использование

1. Откройте приложение в браузере
2. Загрузите два файла для сравнения
3. Нажмите “Сравнить файлы”
4. Результат отобразится в виде двух колонок с подсветкой изменений


## Функции

- Сравнение текстовых файлов (.txt, .py, .js, .json, .csv, .log)
- Сравнение Word-файлов (.docx)
- Автоматическое определение кодировки
- Подсветка:
    - Зеленый: добавленные строки
    - Красный: удаленные строки
    - Оранжевый: измененные строки
    - Серый: совпадающие строки