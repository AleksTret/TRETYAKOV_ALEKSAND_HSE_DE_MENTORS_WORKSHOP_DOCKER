#!/bin/bash

# ==========================================
# Тестирование URL Shortener API
# Использование: ./test_api.sh
# ==========================================

echo "=== ТЕСТИРОВАНИЕ URL SHORTENER API ==="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки статуса
check_status() {
    if [ "$1" -eq 200 ] || [ "$1" -eq 201 ] || [ "$1" -eq 307 ]; then
        echo -e "${GREEN}✓ Успех (код: $1)${NC}"
        return 0
    else
        echo -e "${RED}✗ Ошибка (код: $1)${NC}"
        return 1
    fi
}

# 1. Проверка доступности сервиса
echo -e "\n${YELLOW}1. Проверка доступности сервиса${NC}"
status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
check_status $status_code

# 2. Создание коротких ссылок
echo -e "\n${YELLOW}2. Создание коротких ссылок${NC}"

# Google
echo "Создаем ссылку на Google..."
google_response=$(curl -s -X POST "http://localhost:8080/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}')
echo "Ответ: $google_response"

google_id=$(echo $google_response | grep -o '"short_id":"[^"]*"' | cut -d'"' -f4)

# GitHub
echo -e "\nСоздаем ссылку на GitHub..."
github_response=$(curl -s -X POST "http://localhost:8080/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}')
echo "Ответ: $github_response"

github_id=$(echo $github_response | grep -o '"short_id":"[^"]*"' | cut -d'"' -f4)

# 3. Тест с невалидным URL
echo -e "\n${YELLOW}3. Тест с невалидным URL${NC}"
invalid_response=$(curl -s -w " (код: %{http_code})" -X POST "http://localhost:8080/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "invalid-url"}')
echo "Ответ:$invalid_response"

# 4. Тестирование редиректа
echo -e "\n${YELLOW}4. Тестирование редиректа${NC}"

echo -n "Редирект Google ($google_id): "
google_redirect_code=$(curl -s -o /dev/null -w "%{http_code}" -L "http://localhost:8080/$google_id")
check_status $google_redirect_code

echo -n "Редирект GitHub ($github_id): "
github_redirect_code=$(curl -s -o /dev/null -w "%{http_code}" -L "http://localhost:8080/$github_id")
check_status $github_redirect_code

# 5. Получение статистики
echo -e "\n${YELLOW}5. Получение статистики${NC}"

echo "Статистика Google:"
curl -s "http://localhost:8080/stats/$google_id" | python3 -m json.tool 2>/dev/null || \
  curl -s "http://localhost:8080/stats/$google_id"

echo -e "\nСтатистика GitHub:"
curl -s "http://localhost:8080/stats/$github_id" | python3 -m json.tool 2>/dev/null || \
  curl -s "http://localhost:8080/stats/$github_id"

# 6. Тест несуществующей ссылки
echo -e "\n${YELLOW}6. Тест несуществующей ссылки${NC}"

echo -n "Редирект несуществующей: "
fake_redirect_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/notexist123")
[ $fake_redirect_code -eq 404 ] && echo -e "${GREEN}✓ Ожидаемая ошибка 404${NC}" || echo -e "${RED}✗ Неожиданный код: $fake_redirect_code${NC}"

echo -n "Статистика несуществующей: "
fake_stats_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/stats/notexist123")
[ $fake_stats_code -eq 404 ] && echo -e "${GREEN}✓ Ожидаемая ошибка 404${NC}" || echo -e "${RED}✗ Неожиданный код: $fake_stats_code${NC}"

# 7. Проверка счетчика кликов
echo -e "\n${YELLOW}7. Проверка счетчика кликов${NC}"

echo "Делаем 2 перехода по Google ссылке..."
for i in 1 2; do
    echo "  Клик $i..."
    curl -s -L "http://localhost:8080/$google_id" -o /dev/null
done

echo -e "\nОбновленная статистика Google:"
curl -s "http://localhost:8080/stats/$google_id" | grep -o '"click_count":[0-9]*'

# 8. Итоговый отчет
echo -e "\n${YELLOW}8. Итоговый отчет${NC}"
echo "Созданные ссылки:"
echo "• http://localhost:8080/$google_id → https://google.com"
echo "• http://localhost:8080/$github_id → https://github.com"

echo -e "\n${GREEN}=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===${NC}"