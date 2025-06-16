# Чистый процесс добавления файлов через Git LFS (без ошибок)

### 1. Подготовка репозитория

```powershell
# Установите Git LFS (если не установлен)
git lfs install

# Активируйте отслеживание для нужных файлов/паттернов
git lfs track "*.csv"
git lfs track "*.psd"
git lfs track "binaries/*"

# Проверьте отслеживаемые паттерны
git lfs track
```

### 2. Добавление новых файлов

```powershell
# Шаг 1: Добавьте файлы в LFS-отслеживание
git lfs track "путь/к/файлу/большой_файл.dat"

# Шаг 2: Добавьте .gitattributes в индекс
git add .gitattributes

# Шаг 3: Добавьте сами файлы
git add путь/к/файлу/большой_файл.dat

# Шаг 4: Коммит
git commit -m "Добавлен большой_файл.dat через LFS"
```

### 3. Push на GitHub

```powershell
# Стандартный push
git push origin master

# Если возникает ошибка LFS - проверьте статус
git lfs ls-files
```

## Если файл УЖЕ добавлен в историю без LFS

### 1. Удаление файла из истории

```powershell
# Удалите файл из индекса (но сохраните на диске)
git rm --cached Database/data_test_csv/Grades.csv

# Создайте коммит удаления
git commit -m "Удаление Grades.csv перед LFS"
```

### 2. Добавление через LFS

```powershell
# Включите отслеживание
git lfs track "Database/data_test_csv/Grades.csv"

# Добавьте файл правильно
git add .gitattributes
git add Database/data_test_csv/Grades.csv
git commit -m "Добавлен Grades.csv через LFS"
```

### 3. Синхронизация с удалённым репозиторием

```powershell
# Получите изменения с GitHub
git pull origin master --rebase

# Если есть конфликты - разрешите их, затем:
git rebase --continue

# Push с force (если нужно перезаписать историю)
git push --force-with-lease origin master
```

---

### Проверка корректности LFS

```powershell
# Проверьте управляемые файлы
git lfs ls-files

# Убедитесь, что файл - указатель
cat Database/data_test_csv/Grades.csv
```

### Должен показать LFS-указатель вида

```textline
version https://git-lfs.github.com/spec/v1
oid sha256:894f8a1eef... 
size 237260000
```

### Финальный Push

```powershell
# Стандартный push
git push origin master

# Если не работает - диагностика
git lfs env
git lfs push origin master --all
```

---

💼 **Автор:** Дуплей Максим Игоревич

📲 **Telegram:** @quadd4rv1n7

📅 **Дата:** 12.05.2025

▶️ **Версия 1.0**

```textline
※ Предложения по сотрудничеству можете присылать на почту ※
📧 maksimqwe42@mail.ru
```
