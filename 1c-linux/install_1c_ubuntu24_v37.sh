#!/usr/bin/env bash
# ==============================================================================
# install_1c_ubuntu24_v37.sh
# Универсальный установщик 1С для Ubuntu 24.04 без dialog
#
# Текущие изменения и добавления к версии v37:
# 1. Исправлена ошибка блокировки dpkg/apt: скрипт ждёт unattended-upgrades/apt/dpkg,
#    а после таймаута предлагает принудительно остановить unattended-upgrades.
# 2. Для license-tools добавлена автоматическая установка Java:
#    openjdk-17-jre-headless. Исправляет ошибку:
#    JAVA_HOME environment variable is not set and Java is not found in PATH.
# 3. Поддерживаются старые и новые архивы 1С:
#    *.tar.gz, *.tgz, *.tar, *.zip.
# 4. Поддерживаются старые и новые имена deb-пакетов 1С:
#    1c-enterprise83-*.deb
#    1c-enterprise-8.3.xx.xxxx-*.deb
# 5. В меню всё переведено на русский язык.
# 6. Полная установка включает: 1С + PostgreSQL для 1С + Apache + публикация.
# 7. Добавлена раздельная архитектура:
#    сервер 1С + Apache отдельно, PostgreSQL для 1С отдельно.
# 8. Добавлена регистрация информационной базы в текущем активном кластере.
# 9. Добавлена проверка XML/VRD публикации Apache.
# 10. Имя отчёта формируется с версией 1С и PostgreSQL.
# 11. Добавлено защитное подтверждение для опасных операций удаления:
#     для полного удаления PostgreSQL для 1С и удаления всего нужно вручную ввести 777.
# 12. В краткий отчёт добавлен полный раздел «Логины и пароли»:
#     PostgreSQL admin, postgres, usr1cv8, информационная база 1С, Apache, license-tools,
#     а также последние введённые параметры создания информационной базы.
# 13. Исправлена проверка XML/VRD публикации Apache: устранена ошибка /rac: No such file or directory.
# 14. Исправлена ошибка v27: восстановлены функции create_or_register_infobase_current_cluster
#     и связанные функции, которые отсутствовали в укороченной сборке.
# 15. Исправлено ложное ожидание unattended-upgrade-shutdown --wait-for-signal:
#     скрипт игнорирует этот shutdown-helper и ждёт только реальные блокировки apt/dpkg.
# 16. Исправлена финальная проверка для раздельной архитектуры:
#     если на сервере установлен только PostgreSQL для 1С, скрипт больше не падает
#     с ошибкой «каталог 1С не найден». Финальная проверка теперь отдельно проверяет:
#     PostgreSQL, 1С, RAS, Apache, порты, пакеты и отчёт.
# 17. Добавлен пункт меню «Установка 1С + Apache + публикация» для раздельной схемы.
#     Нумерация меню изменена по новой структуре пользователя.
# 18. Исправлено поведение меню: после выполнения выбранного пункта скрипт не завершается,
#     а возвращается в главное меню. Ошибки пункта показываются на экране и записываются в лог,
#     после чего можно выбрать другой пункт без повторного запуска скрипта.
# 19. Исправлена работа с раздельной архитектурой при создании базы на удалённом PostgreSQL:
#     при установке PostgreSQL пользователь admin получает права SUPERUSER и CREATEDB,
#     чтобы сервер 1С мог создать базу через RAC. При публикации скрипт проверяет права
#     удалённого пользователя PostgreSQL до создания информационной базы и показывает точные
#     команды исправления, если прав недостаточно.
# 20. Исправлена публикация при удалённом PostgreSQL: если на сервере 1С нет клиента psql,
#     скрипт автоматически устанавливает postgresql-client и повторяет проверку прав пользователя.
# 21. Добавлен раздел «Полезные ссылки» в меню и отчёт.
#     Дистрибутивы платформы 1С: https://releases.1c.ru/project/Platform83?allUpdates=true#updates
# 22. Добавлена поддержка дополнительного URL-пути публикации в нижнем регистре.
#     Например основная публикация /1c/XALQ_1C автоматически может получить алиас /1c/xalq_1c.
#     Это устраняет ошибку Apache Not Found, если пользователь открыл URL маленькими буквами.
# ==============================================================================

set -Eeuo pipefail

SCRIPT_VERSION="v37"
LOG_FILE="/var/log/install_1c_ubuntu24_${SCRIPT_VERSION}.log"
RUN_DIR="$(pwd)"
REPORT_BASE_DIR="$RUN_DIR"
WORKDIR="/tmp/1c_install_unpack"

PG_REPO_SCRIPT_URL="https://repo.postgrespro.ru/1c/1c-17/keys/pgpro-repo-add.sh"
PG_PACKAGE="postgrespro-1c-17"
PG_SERVICE="postgrespro-1c-17"
PG_DATA="/var/lib/pgpro/1c-17/data"
PG_CONF="$PG_DATA/postgresql.conf"
PG_HBA="$PG_DATA/pg_hba.conf"

DEFAULT_1C_SERVER_IP="192.168.11.14"
DEFAULT_PG_SERVER_IP="192.168.11.15"
DEFAULT_DB_NAME="xalq_1c"
DEFAULT_DB_USER="admin"
DEFAULT_DB_PASS="CHANGE_ME_STRONG_PASSWORD"
DEFAULT_IB_NAME="XALQ_1C"
DEFAULT_RAGENT_PORT="1540"
DEFAULT_REGPORT="1541"
DEFAULT_RAS_PORT="1545"
DEFAULT_RANGE="1560:1591"

ONEC_DIR=""
ONEC_VERSION="unknown"
PG_VERSION="unknown"
REPORT_FILE="$REPORT_BASE_DIR/1c_install_report_unknown.txt"
CREDENTIALS_FILE="$REPORT_BASE_DIR/1c_last_credentials.env"
LAST_IB_NAME="$DEFAULT_IB_NAME"
LAST_DB_NAME="$DEFAULT_DB_NAME"
LAST_DB_USER="$DEFAULT_DB_USER"
LAST_DB_PASS="$DEFAULT_DB_PASS"
LAST_PG_HOST="127.0.0.1"

exec > >(tee -a "$LOG_FILE") 2>&1
trap 'echo; echo "ОШИБКА в строке $LINENO. Смотрите лог: $LOG_FILE"; exit 1' ERR

print_header() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

pause_enter() {
  echo
  read -r -p "Нажмите Enter для продолжения..." _ || true
}

require_root() {
  if [[ ${EUID} -ne 0 ]]; then
    echo "ОШИБКА: запустите скрипт от root: sudo ./$0"
    exit 1
  fi
}

get_current_ip() {
  hostname -I 2>/dev/null | awk '{print $1}' || true
}

wait_for_apt_locks() {
  print_header "Проверка блокировок apt/dpkg"
  local waited=0
  local max_wait=300

  while true; do
    local lock_busy=0
    local proc_busy=0

    fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 && lock_busy=1
    fuser /var/lib/dpkg/lock >/dev/null 2>&1 && lock_busy=1
    fuser /var/cache/apt/archives/lock >/dev/null 2>&1 && lock_busy=1

    # Ждём только реальные apt/dpkg процессы.
    # unattended-upgrade-shutdown --wait-for-signal — это системный shutdown-helper.
    # Он часто висит в фоне после загрузки/обновлений и обычно НЕ держит dpkg lock.
    # Поэтому его игнорируем, чтобы скрипт не выглядел зависшим.
    if ps -eo comm,args | awk '
      $1 ~ /^(apt|apt-get|dpkg)$/ {found=1}
      $1 ~ /^unattended-upgr/ && $0 !~ /unattended-upgrade-shutdown/ {found=1}
      END {exit found ? 0 : 1}
    '; then
      proc_busy=1
    fi

    if [[ "$lock_busy" -eq 0 && "$proc_busy" -eq 0 ]]; then
      break
    fi

    echo "apt/dpkg занят другим процессом. Ожидание... ${waited}/${max_wait} сек."
    ps -eo pid,comm,args | grep -E 'apt|apt-get|dpkg|unattended-upgr' | grep -v grep || true

    if (( waited >= max_wait )); then
      echo
      echo "Блокировка держится слишком долго. Обычно это unattended-upgrades."
      echo "Если виден только unattended-upgrade-shutdown --wait-for-signal, это не активная установка пакетов."
      read -r -p "Остановить unattended-upgrades и продолжить? [y/N]: " ans
      if [[ "$ans" =~ ^[YyДд]$ ]]; then
        systemctl stop unattended-upgrades 2>/dev/null || true
        pkill -TERM unattended-upgr 2>/dev/null || true
        sleep 5
        pkill -KILL unattended-upgr 2>/dev/null || true
        break
      else
        echo "Остановка по запросу пользователя."
        return 1
      fi
    fi

    sleep 5
    waited=$((waited+5))
  done

  dpkg --configure -a || true
}


apt_install_safe() {
  wait_for_apt_locks
  DEBIAN_FRONTEND=noninteractive apt-get update -y
  wait_for_apt_locks
  DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

install_base_packages() {
  print_header "Установка базовых пакетов"
  apt_install_safe \
    curl wget gnupg2 ca-certificates lsb-release locales software-properties-common \
    tar gzip bzip2 xz-utils unzip openssh-server nano mc htop net-tools iproute2 \
    psmisc procps perl libc6 libgcc-s1 libstdc++6 libxml2 zlib1g libicu74 \
    libssl3t64 liblz4-1 libzstd1 libfreetype6 libfontconfig1 libglib2.0-0t64 \
    libgtk-3-0t64 libx11-6 libxext6 libxrender1 libxtst6 libsm6 libice6 \
    unixodbc imagemagick fontconfig openjdk-17-jre-headless

  locale-gen ru_RU.UTF-8 || true
  update-locale LANG=ru_RU.UTF-8 || true
  export LANG=ru_RU.UTF-8
}

ensure_usr1cv8() {
  print_header "Проверка/создание системного пользователя 1С"
  if ! getent group grp1cv8 >/dev/null 2>&1; then
    groupadd -r grp1cv8 || true
  fi
  if ! id -u usr1cv8 >/dev/null 2>&1; then
    useradd -r -m -g grp1cv8 -s /bin/bash usr1cv8
  fi
  mkdir -p /home/usr1cv8/.1cv8/srvinfo /var/1C/licenses /home/usr1cv8/.1cv8/1C/1cv8/conf
  chown -R usr1cv8:grp1cv8 /home/usr1cv8 /var/1C || true
  chmod -R 775 /var/1C/licenses || true
}

find_archives() {
  find "$RUN_DIR" -maxdepth 1 -type f \( \
    -iname "*.tar.gz" -o -iname "*.tgz" -o -iname "*.tar" -o -iname "*.zip" \
  \) | sort
}

select_1c_archive() {
  mapfile -t archives < <(find_archives)
  if (( ${#archives[@]} == 0 )); then
    echo "ОШИБКА: в текущем каталоге не найдены архивы 1С: *.tar.gz, *.tgz, *.tar, *.zip"
    return 1
  fi
  echo
  echo "Найдены архивы 1С в текущем каталоге:"
  local i=1
  for a in "${archives[@]}"; do
    echo "  $i) $(basename "$a")"
    i=$((i+1))
  done
  echo
  read -r -p "Выберите номер архива: " n
  if ! [[ "$n" =~ ^[0-9]+$ ]] || (( n < 1 || n > ${#archives[@]} )); then
    echo "ОШИБКА: неверный номер архива"
    return 1
  fi
  SELECTED_ARCHIVE="${archives[$((n-1))]}"
  echo "Выбрано: $SELECTED_ARCHIVE"
}

extract_archive() {
  print_header "Распаковка архива 1С"
  rm -rf "$WORKDIR"
  mkdir -p "$WORKDIR"
  echo "Архив: $SELECTED_ARCHIVE"
  echo "Рабочий каталог: $WORKDIR"
  case "${SELECTED_ARCHIVE,,}" in
    *.zip) unzip -q "$SELECTED_ARCHIVE" -d "$WORKDIR" ;;
    *.tar.gz|*.tgz) tar -xzf "$SELECTED_ARCHIVE" -C "$WORKDIR" ;;
    *.tar) tar -xf "$SELECTED_ARCHIVE" -C "$WORKDIR" ;;
    *) echo "ОШИБКА: неизвестный тип архива"; return 1 ;;
  esac
  echo "Распакованные файлы:"
  find "$WORKDIR" -maxdepth 3 -type f | sed 's/^/  /' | head -n 120 || true
}

install_license_tools_from_unpack() {
  print_header "Установка/копирование инструментов лицензирования 1С, если они есть"
  local lt
  lt="$(find "$WORKDIR" -type d -name license-tools | head -n1 || true)"
  if [[ -z "$lt" ]]; then
    echo "Папка license-tools в архиве не найдена. Пропускаем."
    return 0
  fi
  echo "Найден license-tools: $lt"
  rm -rf /opt/1C/license-tools
  mkdir -p /opt/1C
  cp -a "$lt" /opt/1C/license-tools
  chmod +x /opt/1C/license-tools/1ce-installer 2>/dev/null || true
  chmod +x /opt/1C/license-tools/1ce-installer-cli 2>/dev/null || true
  ln -sf /opt/1C/license-tools/1ce-installer /usr/local/bin/1ce-installer 2>/dev/null || true
  ln -sf /opt/1C/license-tools/1ce-installer-cli /usr/local/bin/1ce-installer-cli 2>/dev/null || true
  echo "Инструменты лицензирования скопированы в: /opt/1C/license-tools"
  echo "Проверка Java:"
  java -version || true
  echo "Проверка 1ce-installer-cli:"
  /usr/local/bin/1ce-installer-cli --help 2>&1 | head -n 30 || true
}

install_1c_debs_from_unpack() {
  print_header "Поиск .deb-пакетов 1С после распаковки"
  mapfile -t debs < <(find "$WORKDIR" -type f -name "*.deb" | sort)
  if (( ${#debs[@]} == 0 )); then
    echo "ОШИБКА: .deb-пакеты 1С после распаковки не найдены"
    return 1
  fi
  printf '  %s\n' "${debs[@]##*/}"

  print_header "Установка .deb-пакетов 1С"
  wait_for_apt_locks
  dpkg -i "${debs[@]}" || true
  wait_for_apt_locks
  DEBIAN_FRONTEND=noninteractive apt-get -f install -y
  wait_for_apt_locks
  dpkg -i "${debs[@]}"
}

detect_1c_path() {
  print_header "Определение установленного каталога 1С"
  ONEC_DIR=""
  if [[ -d /opt/1C/v8.3/x86_64 ]]; then
    ONEC_DIR="/opt/1C/v8.3/x86_64"
  elif [[ -d /opt/1cv8/x86_64 ]]; then
    ONEC_DIR="$(find /opt/1cv8/x86_64 -maxdepth 1 -mindepth 1 -type d | sort -V | tail -n1 || true)"
  fi
  if [[ -z "$ONEC_DIR" || ! -x "$ONEC_DIR/ragent" ]]; then
    echo "ОШИБКА: каталог 1С не найден. Проверены /opt/1C/v8.3/x86_64 и /opt/1cv8/x86_64"
    return 1
  fi
  echo "Найден каталог 1С: $ONEC_DIR"
  ONEC_VERSION="$($ONEC_DIR/ragent -v 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || true)"
  if [[ -z "$ONEC_VERSION" ]]; then
    ONEC_VERSION="$(dpkg-query -W -f='${Version}\n' '1c-enterprise*server*' 2>/dev/null | head -n1 || echo unknown)"
  fi
  echo "Версия 1С: ${ONEC_VERSION:-unknown}"
  chown -R usr1cv8:grp1cv8 /home/usr1cv8 /var/1C || true
}

configure_1c_services() {
  print_header "Настройка служб 1С ragent и RAS"
  detect_1c_path
  cat > /etc/systemd/system/1c-ragent.service <<EOF2
[Unit]
Description=1C Enterprise Server Agent
After=network.target

[Service]
Type=forking
User=usr1cv8
Group=grp1cv8
ExecStart=${ONEC_DIR}/ragent -daemon -port ${DEFAULT_RAGENT_PORT} -regport ${DEFAULT_REGPORT} -range ${DEFAULT_RANGE} -d /home/usr1cv8/.1cv8/srvinfo
ExecStop=/usr/bin/pkill -f '${ONEC_DIR}/ragent'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF2

  cat > /etc/systemd/system/ras83.service <<EOF2
[Unit]
Description=1C Enterprise Remote Administration Server
After=network.target 1c-ragent.service
Requires=1c-ragent.service

[Service]
Type=forking
User=usr1cv8
Group=grp1cv8
ExecStart=${ONEC_DIR}/ras cluster --daemon --port=${DEFAULT_RAS_PORT} localhost:${DEFAULT_RAGENT_PORT}
ExecStop=/usr/bin/pkill -f '${ONEC_DIR}/ras'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF2

  systemctl daemon-reload
  systemctl enable 1c-ragent ras83
  systemctl restart 1c-ragent
  sleep 7
  systemctl restart ras83
  sleep 3
  systemctl status 1c-ragent --no-pager -l || true
  systemctl status ras83 --no-pager -l || true
}

install_postgresql_1c() {
  print_header "Установка PostgreSQL для 1С: Postgres Pro 1C 17"
  install_base_packages
  wait_for_apt_locks

  if systemctl list-unit-files | grep -q "^${PG_SERVICE}.service"; then
    echo "PostgreSQL для 1С уже установлен: $PG_SERVICE"
  else
    echo "Проверка репозитория Postgres Pro 1C 17"
    if [[ -f /etc/apt/sources.list.d/postgresql-1c-17.list ]] || grep -R "repo.postgrespro.ru/1c/1c-17" /etc/apt/sources.list /etc/apt/sources.list.d/*.list >/dev/null 2>&1; then
      echo "Репозиторий Postgres Pro 1C 17 уже добавлен. Повторно не добавляем."
    else
      curl -fsSL "$PG_REPO_SCRIPT_URL" -o /tmp/pgpro-repo-add.sh
      bash /tmp/pgpro-repo-add.sh
    fi
    DEBIAN_FRONTEND=noninteractive apt-get update -y
    apt_install_safe "$PG_PACKAGE"
  fi

  configure_postgresql_1c
}
configure_postgresql_1c() {
  print_header "Настройка PostgreSQL для 1С"
  systemctl enable "$PG_SERVICE"
  systemctl restart "$PG_SERVICE"
  sleep 3
  if [[ ! -f "$PG_CONF" || ! -f "$PG_HBA" ]]; then
    echo "ОШИБКА: не найдены файлы конфигурации PostgreSQL: $PG_CONF, $PG_HBA"
    return 1
  fi
  sed -i "s/^#\?listen_addresses.*/listen_addresses = '*'/" "$PG_CONF" || true
  if grep -q '^#\?password_encryption' "$PG_CONF"; then
    sed -i "s/^#\?password_encryption.*/password_encryption = md5/" "$PG_CONF"
  else
    echo "password_encryption = md5" >> "$PG_CONF"
  fi

  local current_ip allow_ip
  current_ip="$(get_current_ip)"
  echo "Текущий IP сервера: ${current_ip:-не определён}"
  read -r -p "IP сервера 1С, которому разрешить доступ к PostgreSQL [${DEFAULT_1C_SERVER_IP}]: " allow_ip
  allow_ip="${allow_ip:-$DEFAULT_1C_SERVER_IP}"

  cat > "$PG_HBA" <<EOF2
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             ${allow_ip}/32          md5
host    all             all             0.0.0.0/0               md5
host    all             all             ::/0                    md5
EOF2

  systemctl restart "$PG_SERVICE"
  sleep 3

  sudo -u postgres psql <<EOF2
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='${DEFAULT_DB_USER}') THEN
      CREATE ROLE ${DEFAULT_DB_USER} LOGIN SUPERUSER CREATEDB PASSWORD '${DEFAULT_DB_PASS}';
   ELSE
      ALTER ROLE ${DEFAULT_DB_USER} WITH LOGIN SUPERUSER CREATEDB PASSWORD '${DEFAULT_DB_PASS}';
   END IF;
END
\$\$;
ALTER ROLE ${DEFAULT_DB_USER} WITH SUPERUSER CREATEDB;
EOF2

  PG_VERSION="$(sudo -u postgres psql -tAc 'select version();' 2>/dev/null | head -n1 || echo unknown)"
  echo "PostgreSQL версия: $PG_VERSION"
}

install_apache_only() {
  print_header "Установка Apache"
  apt_install_safe apache2
  a2enmod headers rewrite proxy proxy_http >/dev/null 2>&1 || true
  systemctl enable apache2
  systemctl restart apache2
}

get_cluster_id() {
  detect_1c_path >/dev/null
  "$ONEC_DIR/rac" cluster list localhost:${DEFAULT_RAS_PORT} | awk -F': ' '/^cluster[[:space:]]*:/ {print $2; exit}'
}


check_pg_user_rights_for_1c() {
  local pg_host="$1" db_user="$2" db_pass="$3"
  local role_info rolsuper rolcreatedb

  print_header "Проверка прав пользователя PostgreSQL для создания базы 1С"
  echo "PostgreSQL host: ${pg_host}"
  echo "Пользователь: ${db_user}"

  if [[ "$pg_host" == "127.0.0.1" || "$pg_host" == "localhost" ]]; then
    sudo -u postgres psql -tAc "ALTER ROLE ${db_user} WITH SUPERUSER CREATEDB;" >/dev/null 2>&1 || true
    echo "Локальный PostgreSQL: права SUPERUSER и CREATEDB выданы пользователю ${db_user}."
    return 0
  fi

  if ! command -v psql >/dev/null 2>&1; then
    echo "На сервере 1С не найден клиент psql. Устанавливаем postgresql-client автоматически..."
    if ! apt_install_safe postgresql-client; then
      echo "Не удалось установить пакет postgresql-client. Пробуем установить postgresql-client-16..."
      apt_install_safe postgresql-client-16 || true
    fi
  fi

  if ! command -v psql >/dev/null 2>&1; then
    echo "ОШИБКА: клиент psql всё ещё не найден."
    echo "Установите вручную на сервере 1С:"
    echo "  apt-get update && apt-get install -y postgresql-client"
    return 1
  fi

  role_info="$(PGPASSWORD="$db_pass" psql -h "$pg_host" -U "$db_user" -d postgres -Atc "SELECT rolsuper || '|' || rolcreatedb FROM pg_roles WHERE rolname=current_user;" 2>/dev/null || true)"

  if [[ -z "$role_info" ]]; then
    echo "ОШИБКА: не удалось подключиться к PostgreSQL ${pg_host} пользователем ${db_user}."
    echo
    echo "Проверьте на сервере PostgreSQL:"
    echo "  1) сервис postgrespro-1c-17 запущен;"
    echo "  2) в postgresql.conf: listen_addresses = '*';"
    echo "  3) в pg_hba.conf разрешён IP сервера 1С;"
    echo "  4) пароль пользователя ${db_user} правильный."
    return 1
  fi

  rolsuper="${role_info%%|*}"
  rolcreatedb="${role_info##*|}"
  echo "rolsuper=${rolsuper}"
  echo "rolcreatedb=${rolcreatedb}"

  if [[ "$rolsuper" == "t" || "$rolsuper" == "true" || "$rolsuper" == "1" || "$rolcreatedb" == "t" || "$rolcreatedb" == "true" || "$rolcreatedb" == "1" ]]; then
    echo "Права достаточные: пользователь может создать базу PostgreSQL для 1С."
    return 0
  fi

  echo
  echo "ОШИБКА: у пользователя ${db_user} недостаточно прав для создания базы через сервер 1С."
  echo "На сервере PostgreSQL (${pg_host}) выполните один из вариантов:"
  echo
  echo "Вариант 1 — через этот установщик на сервере PostgreSQL:"
  echo "  sudo ./install_1c_ubuntu24_v36.sh"
  echo "  выбрать пункт 4) Установка только PostgreSQL для 1С"
  echo
  echo "Вариант 2 — вручную на сервере PostgreSQL:"
  echo "  sudo -u postgres psql -c \"ALTER ROLE ${db_user} WITH SUPERUSER CREATEDB PASSWORD '${db_pass}';\""
  echo
  echo "После этого снова запустите публикацию/создание базы на сервере 1С."
  return 1
}

create_or_register_infobase_current_cluster() {
  print_header "Создание/регистрация информационной базы в текущем активном кластере"
  detect_1c_path
  systemctl restart 1c-ragent
  sleep 7
  systemctl restart ras83
  sleep 3
  local cluster_id pg_host db_name db_user db_pass ib_name drop_db
  cluster_id="$(get_cluster_id)"
  if [[ -z "$cluster_id" ]]; then
    echo "ОШИБКА: не удалось определить CLUSTER_ID"
    return 1
  fi
  echo "Текущий активный CLUSTER_ID: $cluster_id"
  echo "Список баз до операции:"
  "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true

  read -r -p "Имя информационной базы [${DEFAULT_IB_NAME}]: " ib_name; ib_name="${ib_name:-$DEFAULT_IB_NAME}"
  read -r -p "Имя базы PostgreSQL [${DEFAULT_DB_NAME}]: " db_name; db_name="${db_name:-$DEFAULT_DB_NAME}"
  read -r -p "Пользователь PostgreSQL [${DEFAULT_DB_USER}]: " db_user; db_user="${db_user:-$DEFAULT_DB_USER}"
  read -r -s -p "Пароль PostgreSQL [скрыт, Enter = пароль по умолчанию]: " db_pass; echo; db_pass="${db_pass:-$DEFAULT_DB_PASS}"
  read -r -p "IP/host PostgreSQL [127.0.0.1 или ${DEFAULT_PG_SERVER_IP}] [127.0.0.1]: " pg_host; pg_host="${pg_host:-127.0.0.1}"

  LAST_IB_NAME="$ib_name"
  LAST_DB_NAME="$db_name"
  LAST_DB_USER="$db_user"
  LAST_DB_PASS="$db_pass"
  LAST_PG_HOST="$pg_host"
  cat > "$CREDENTIALS_FILE" <<EOF_CRED
LAST_IB_NAME='$ib_name'
LAST_DB_NAME='$db_name'
LAST_DB_USER='$db_user'
LAST_DB_PASS='$db_pass'
LAST_PG_HOST='$pg_host'
LAST_CLUSTER_ID='$cluster_id'
EOF_CRED
  chmod 600 "$CREDENTIALS_FILE" || true

  if "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} | grep -q "name[[:space:]]*:[[:space:]]*${ib_name}"; then
    echo "Информационная база ${ib_name} уже зарегистрирована в текущем кластере."
    return 0
  fi

  read -r -p "Удалить существующую PostgreSQL DB ${db_name} перед созданием? [y/N]: " drop_db
  if [[ "$pg_host" == "127.0.0.1" || "$pg_host" == "localhost" ]]; then
    if id postgres >/dev/null 2>&1; then
      sudo -u postgres psql -c "ALTER ROLE ${db_user} WITH SUPERUSER CREATEDB;" || true
      if [[ "$drop_db" =~ ^[YyДд]$ ]]; then
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${db_name};" || true
      fi
    else
      echo "ВНИМАНИЕ: локальный пользователь postgres не найден. Вероятно PostgreSQL установлен на другом сервере."
      echo "Укажите IP удалённого PostgreSQL, например ${DEFAULT_PG_SERVER_IP}, а не 127.0.0.1."
    fi
  else
    echo "PostgreSQL удалённый (${pg_host}); локальные команды sudo -u postgres на сервере 1С не выполняются."
    if [[ "$drop_db" =~ ^[YyДд]$ ]]; then
      echo "Удаление удалённой PostgreSQL DB из этого пункта не выполняется автоматически. При необходимости удалите базу на сервере PostgreSQL вручную."
    fi
  fi

  check_pg_user_rights_for_1c "$pg_host" "$db_user" "$db_pass"

  "$ONEC_DIR/rac" infobase create \
    --cluster="$cluster_id" \
    --create-database \
    --name="$ib_name" \
    --dbms=PostgreSQL \
    --db-server="$pg_host" \
    --db-name="$db_name" \
    --db-user="$db_user" \
    --db-pwd="$db_pass" \
    --locale=ru \
    localhost:${DEFAULT_RAS_PORT}

  sudo -u postgres psql -c "ALTER ROLE ${db_user} WITH NOSUPERUSER;" || true
  echo "Список баз после операции:"
  "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true
}

ensure_infobase_exists_for_publication() {
  local ib_name="$1"
  local cluster_id db_name db_user db_pass pg_host answer

  print_header "Проверка информационной базы в текущем активном кластере"
  detect_1c_path

  systemctl restart 1c-ragent 2>/dev/null || true
  sleep 5
  systemctl restart ras83 2>/dev/null || true
  sleep 3

  cluster_id="$(get_cluster_id || true)"
  if [[ -z "${cluster_id:-}" ]]; then
    echo "ОШИБКА: не удалось определить текущий активный CLUSTER_ID."
    echo "Проверьте службы: systemctl status 1c-ragent ras83"
    return 1
  fi

  echo "Текущий активный CLUSTER_ID: ${cluster_id}"
  echo "Список информационных баз в текущем кластере:"
  "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true

  if "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} | grep -q "name[[:space:]]*:[[:space:]]*${ib_name}"; then
    echo "Информационная база ${ib_name} уже есть в текущем активном кластере."
    LAST_IB_NAME="$ib_name"
    return 0
  fi

  echo
  echo "Информационная база ${ib_name} НЕ найдена в текущем активном кластере."
  echo "Это частая ситуация при раздельной установке: PostgreSQL отдельно, 1С + Apache отдельно."
  read -r -p "Создать/зарегистрировать базу сейчас? [Y/n]: " answer
  answer="${answer:-Y}"
  if [[ ! "$answer" =~ ^[YyДд]$ ]]; then
    echo "Создание базы отменено. Публикация может показать: Информационная база не обнаружена."
    return 0
  fi

  read -r -p "Имя базы PostgreSQL [${DEFAULT_DB_NAME}]: " db_name; db_name="${db_name:-$DEFAULT_DB_NAME}"
  read -r -p "Пользователь PostgreSQL [${DEFAULT_DB_USER}]: " db_user; db_user="${db_user:-$DEFAULT_DB_USER}"
  read -r -s -p "Пароль PostgreSQL [скрыт, Enter = пароль по умолчанию]: " db_pass; echo; db_pass="${db_pass:-$DEFAULT_DB_PASS}"
  read -r -p "IP/host PostgreSQL [127.0.0.1 или ${DEFAULT_PG_SERVER_IP}] [${DEFAULT_PG_SERVER_IP}]: " pg_host; pg_host="${pg_host:-$DEFAULT_PG_SERVER_IP}"

  LAST_IB_NAME="$ib_name"
  LAST_DB_NAME="$db_name"
  LAST_DB_USER="$db_user"
  LAST_DB_PASS="$db_pass"
  LAST_PG_HOST="$pg_host"

  cat > "$CREDENTIALS_FILE" <<EOF_CRED
LAST_IB_NAME='$ib_name'
LAST_DB_NAME='$db_name'
LAST_DB_USER='$db_user'
LAST_DB_PASS='$db_pass'
LAST_PG_HOST='$pg_host'
LAST_CLUSTER_ID='$cluster_id'
EOF_CRED
  chmod 600 "$CREDENTIALS_FILE" || true

  if [[ "$pg_host" == "127.0.0.1" || "$pg_host" == "localhost" ]]; then
    sudo -u postgres psql -c "ALTER ROLE ${db_user} WITH SUPERUSER CREATEDB;" || true
  else
    echo "PostgreSQL указан как удалённый сервер: ${pg_host}"
    echo "Проверяем, что на сервере PostgreSQL разрешён доступ и у пользователя есть права CREATEDB/SUPERUSER."
  fi

  check_pg_user_rights_for_1c "$pg_host" "$db_user" "$db_pass"

  "$ONEC_DIR/rac" infobase create \
    --cluster="$cluster_id" \
    --create-database \
    --name="$ib_name" \
    --dbms=PostgreSQL \
    --db-server="$pg_host" \
    --db-name="$db_name" \
    --db-user="$db_user" \
    --db-pwd="$db_pass" \
    --locale=ru \
    localhost:${DEFAULT_RAS_PORT}

  if [[ "$pg_host" == "127.0.0.1" || "$pg_host" == "localhost" ]]; then
    sudo -u postgres psql -c "ALTER ROLE ${db_user} WITH NOSUPERUSER;" || true
  fi

  echo "Список информационных баз после операции:"
  "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true
}

publish_infobase_apache() {
  print_header "Публикация информационной базы 1С в Apache"
  detect_1c_path
  local ib_name base_dir conf_file wsdir connstr

  read -r -p "Имя информационной базы для публикации [${DEFAULT_IB_NAME}]: " ib_name
  ib_name="${ib_name:-$DEFAULT_IB_NAME}"

  ensure_infobase_exists_for_publication "$ib_name"

  install_apache_only
  detect_1c_path
  wsdir="1c/${ib_name}"
  base_dir="/var/www/1c/${ib_name}"
  conf_file="/etc/apache2/conf-available/${ib_name}.conf"
  mkdir -p "$base_dir"
  touch "$conf_file"
  connstr="Srvr=localhost;Ref=${ib_name}"
  "$ONEC_DIR/webinst" -apache24 -wsdir "$wsdir" -dir "$base_dir" -connstr "$connstr" -confPath "$conf_file"
  a2enconf "${ib_name}.conf" >/dev/null 2>&1 || a2enconf "$ib_name" >/dev/null 2>&1 || true
  systemctl reload apache2
  echo "Публикация готова: http://$(get_current_ip)/1c/${ib_name}/"

  local make_lower_alias lower_alias
  lower_alias="$(echo "$ib_name" | tr '[:upper:]' '[:lower:]')"
  if [[ "$lower_alias" != "$ib_name" ]]; then
    read -r -p "Создать также адрес маленькими буквами /1c/${lower_alias}/ ? [Y/n]: " make_lower_alias
    make_lower_alias="${make_lower_alias:-Y}"
    if [[ "$make_lower_alias" =~ ^[YyДд]$ ]]; then
      publish_infobase_lowercase_alias "$ib_name" "$lower_alias"
    fi
  fi
}

publish_infobase_lowercase_alias() {
  print_header "Создание дополнительной публикации 1С маленькими буквами"
  detect_1c_path
  local ib_name alias_name alias_name_input base_dir conf_file wsdir connstr

  ib_name="${1:-}"
  alias_name="${2:-}"

  if [[ -z "$ib_name" ]]; then
    read -r -p "Реальное имя информационной базы в кластере [${DEFAULT_IB_NAME}]: " ib_name
    ib_name="${ib_name:-$DEFAULT_IB_NAME}"
  fi

  if [[ -z "$alias_name" ]]; then
    alias_name="$(echo "$ib_name" | tr '[:upper:]' '[:lower:]')"
    read -r -p "URL-алиас для Apache [${alias_name}]: " alias_name_input
    alias_name="${alias_name_input:-$alias_name}"
  fi

  if [[ "$alias_name" == "$ib_name" ]]; then
    echo "Алиас совпадает с основным именем. Дополнительная публикация не нужна."
    return 0
  fi

  ensure_infobase_exists_for_publication "$ib_name"
  install_apache_only
  detect_1c_path

  wsdir="1c/${alias_name}"
  base_dir="/var/www/1c/${alias_name}"
  conf_file="/etc/apache2/conf-available/${alias_name}.conf"
  mkdir -p "$base_dir"
  touch "$conf_file"
  connstr="Srvr=localhost;Ref=${ib_name}"

  "$ONEC_DIR/webinst" \
    -apache24 \
    -wsdir "$wsdir" \
    -dir "$base_dir" \
    -connstr "$connstr" \
    -confPath "$conf_file"

  a2enconf "${alias_name}.conf" >/dev/null 2>&1 || a2enconf "$alias_name" >/dev/null 2>&1 || true
  systemctl reload apache2

  echo "Основная база в кластере: ${ib_name}"
  echo "Дополнительный URL-адрес: http://$(get_current_ip)/1c/${alias_name}/"
  echo "Важно: Ref остаётся ${ib_name}, меняется только URL-путь Apache."
}

check_publication_xml_vrd() {
  print_header "Проверка XML/VRD публикации Apache"
  local files f
  mapfile -t files < <(find /var/www /etc/apache2* -type f \( -name "*.vrd" -o -name "default.vrd" -o -name "*.xml" -o -name "*.conf" \) 2>/dev/null | sort)
  if (( ${#files[@]} == 0 )); then
    echo "Файлы публикации не найдены."
    return 0
  fi
  for f in "${files[@]}"; do
    if grep -qE 'base=|ib=|Ref=|Srvr=' "$f" 2>/dev/null; then
      echo
      echo "Файл: $f"
      grep -nE 'base=|ib=|Ref=|Srvr=|enableCheckServerLicense' "$f" || true
    fi
  done
  echo
  echo "Проверка баз в активном кластере:"
  local cluster_id

  # Важно: detect_1c_path должен выполняться в текущем shell.
  # Иначе ONEC_DIR может остаться пустой, и команда превратится в /rac.
  if ! detect_1c_path >/dev/null 2>&1; then
    echo "ОШИБКА: каталог 1С не найден, проверка списка баз невозможна."
    return 0
  fi

  cluster_id="$($ONEC_DIR/rac cluster list localhost:${DEFAULT_RAS_PORT} | awk -F': ' '/^cluster[[:space:]]*:/ {print $2; exit}' || true)"
  echo "CLUSTER_ID=${cluster_id:-не найден}"
  if [[ -n "${cluster_id:-}" ]]; then
    "$ONEC_DIR/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true
  fi
}

license_check() {
  print_header "Проверка лицензии / диагностика HASP"
  echo "Каталоги лицензий:"
  ls -lah /var/1C/licenses 2>/dev/null || true
  ls -lah /home/usr1cv8/.1cv8/1C/1cv8/conf 2>/dev/null || true
  echo
  echo "Поиск *.lic:"
  find /var/1C /home/usr1cv8 -name "*.lic" 2>/dev/null || true
  echo
  echo "USB устройства:"
  lsusb || true
  echo
  systemctl status hasplmd --no-pager -l 2>/dev/null || true
  systemctl status aksusbd --no-pager -l 2>/dev/null || true
}

license_tools_check() {
  print_header "Проверка license-tools 1С"
  echo "Ожидаемый каталог: /opt/1C/license-tools"
  if [[ -d /opt/1C/license-tools ]]; then
    find /opt/1C/license-tools -maxdepth 2 -type f | sed 's/^/  /' | head -n 80
    echo
    java -version || true
    /opt/1C/license-tools/1ce-installer-cli --help 2>&1 | head -n 40 || true
  else
    echo "Каталог /opt/1C/license-tools пока не установлен/не скопирован."
  fi
  echo
  echo "Поиск известных инструментов лицензирования/ring:"
  for d in /opt/1C /opt/1cv8 /usr/local/bin; do
    [[ -d "$d" ]] && find "$d" -type f \( -name "ring" -o -name "1ce-installer*" -o -iname "*license*" \) 2>/dev/null | sed 's/^/  /'
  done
}

confirm_777() {
  local action="$1"
  echo
  echo "ВНИМАНИЕ: опасная операция: ${action}"
  echo "Для подтверждения вручную введите: 777"
  read -r -p "Подтверждение: " confirm_code
  if [[ "${confirm_code}" != "777" ]]; then
    echo "Операция отменена. Код подтверждения не совпал."
    return 1
  fi
  echo "Подтверждение принято. Продолжаем."
  return 0
}

remove_1c() {
  print_header "Удаление 1С"
  systemctl stop ras83 1c-ragent 2>/dev/null || true
  systemctl disable ras83 1c-ragent 2>/dev/null || true
  rm -f /etc/systemd/system/ras83.service /etc/systemd/system/1c-ragent.service
  systemctl daemon-reload
  wait_for_apt_locks
  dpkg -l | awk '/1c-enterprise/ {print $2}' | xargs -r apt-get purge -y
  rm -rf /opt/1C/v8.3 /opt/1cv8
}

remove_pg() {
  print_header "Полное удаление PostgreSQL для 1С"
  systemctl stop "$PG_SERVICE" 2>/dev/null || true
  wait_for_apt_locks
  apt-get purge -y 'postgrespro-1c-*' || true
  rm -rf /var/lib/pgpro/1c-17
}

remove_all() {
  remove_1c
  remove_pg
  apt-get purge -y apache2 || true
}

detect_1c_path_optional() {
  ONEC_DIR=""
  ONEC_VERSION="unknown"

  if [[ -d /opt/1C/v8.3/x86_64 && -x /opt/1C/v8.3/x86_64/ragent ]]; then
    ONEC_DIR="/opt/1C/v8.3/x86_64"
  elif [[ -d /opt/1cv8/x86_64 ]]; then
    ONEC_DIR="$(find /opt/1cv8/x86_64 -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort -V | tail -n1 || true)"
  fi

  if [[ -n "${ONEC_DIR:-}" && -x "${ONEC_DIR}/ragent" ]]; then
    ONEC_VERSION="$(${ONEC_DIR}/ragent -v 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || true)"
    if [[ -z "${ONEC_VERSION:-}" ]]; then
      ONEC_VERSION="$(dpkg-query -W -f='${Version}\n' '1c-enterprise*server*' 2>/dev/null | head -n1 || echo unknown)"
    fi
    return 0
  fi

  return 1
}

final_check() {
  print_header "Финальная проверка"
  echo "Текущий сервер: $(hostname)"
  echo "Текущий IP: $(get_current_ip)"
  echo

  echo "Проверка PostgreSQL для 1С:"
  if systemctl list-unit-files 2>/dev/null | grep -q "^${PG_SERVICE}\.service"; then
    systemctl status "$PG_SERVICE" --no-pager -l || true
    sudo -u postgres psql -tAc 'select version();' 2>/dev/null | head -n1 | sed 's/^/Версия PostgreSQL: /' || true
    echo "Проверка пользователя PostgreSQL ${DEFAULT_DB_USER}:"
    sudo -u postgres psql -tAc "select rolname from pg_roles where rolname='${DEFAULT_DB_USER}';" 2>/dev/null | sed 's/^/  /' || true
  else
    echo "PostgreSQL для 1С не установлен или сервис ${PG_SERVICE} не найден."
  fi
  echo

  echo "Проверка 1С:"
  if detect_1c_path_optional; then
    echo "Каталог 1С: ${ONEC_DIR}"
    echo "Версия 1С: ${ONEC_VERSION:-unknown}"
    systemctl status 1c-ragent --no-pager -l || true
    systemctl status ras83 --no-pager -l || true
    local cluster_id
    cluster_id="$(get_cluster_id || true)"
    echo "CLUSTER_ID=${cluster_id:-не найден}"
    if [[ -n "${cluster_id:-}" && -x "${ONEC_DIR}/rac" ]]; then
      "${ONEC_DIR}/rac" infobase summary list --cluster="$cluster_id" localhost:${DEFAULT_RAS_PORT} || true
    fi
  else
    echo "1С на этом сервере не найдена. Это нормально, если этот сервер используется только как PostgreSQL-сервер."
  fi
  echo

  echo "Проверка Apache:"
  if systemctl list-unit-files 2>/dev/null | grep -q '^apache2\.service'; then
    systemctl status apache2 --no-pager -l || true
  else
    echo "Apache не установлен. Это нормально для отдельного PostgreSQL-сервера."
  fi
  echo

  echo "Открытые порты:"
  ss -tulpn | egrep '5432|1540|1541|1545|80|443' || true
  echo

  echo "Установленные пакеты 1С/PostgreSQL/Apache:"
  dpkg -l | awk '/1c-enterprise|postgrespro-1c|apache2/ {print $2, $3}' || true

  write_report
}
write_report() {
  print_header "Создание краткого отчёта"
  detect_1c_path >/dev/null 2>&1 || true
  PG_VERSION="$(sudo -u postgres psql -tAc 'select version();' 2>/dev/null | head -n1 || echo unknown)"
  if [[ -f "$CREDENTIALS_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CREDENTIALS_FILE" || true
  fi
  local safe_1c safe_pg
  safe_1c="$(echo "${ONEC_VERSION:-unknown}" | tr ' /:' '___')"
  safe_pg="$(echo "${PG_VERSION:-unknown}" | grep -oE 'Postgres[^,]+' | head -n1 | tr ' /:' '___' || echo postgres_unknown)"
  REPORT_FILE="$REPORT_BASE_DIR/1c_install_report_1c_${safe_1c}_pg_${safe_pg}.txt"
  cat > "$REPORT_FILE" <<EOF2
============================================================
КРАТКИЙ ОТЧЁТ УСТАНОВКИ 1С / PostgreSQL / Apache
============================================================
Дата: $(date)
Версия скрипта: ${SCRIPT_VERSION}
Каталог запуска: ${RUN_DIR}
Лог: ${LOG_FILE}

АРХИТЕКТУРА ПО УМОЛЧАНИЮ:
1С + Apache сервер: ${DEFAULT_1C_SERVER_IP}
PostgreSQL сервер : ${DEFAULT_PG_SERVER_IP}
Текущий IP сервера: $(get_current_ip)

1С:
Каталог 1С: ${ONEC_DIR:-не найден}
Версия 1С: ${ONEC_VERSION:-unknown}
Установленные пакеты 1С:
$(dpkg -l | awk '/1c-enterprise/ {print $2" "$3}' || true)

PostgreSQL для 1С:
Сервис: ${PG_SERVICE}
Версия: ${PG_VERSION}
Пользователь БД по умолчанию: ${DEFAULT_DB_USER}
Пароль БД по умолчанию: ${DEFAULT_DB_PASS}
База PostgreSQL по умолчанию: ${DEFAULT_DB_NAME}
Информационная база 1С по умолчанию: ${DEFAULT_IB_NAME}
Последний PostgreSQL host/IP: ${LAST_PG_HOST:-127.0.0.1}
Последний пользователь БД: ${LAST_DB_USER:-$DEFAULT_DB_USER}
Последний пароль БД: ${LAST_DB_PASS:-$DEFAULT_DB_PASS}
Последняя база PostgreSQL: ${LAST_DB_NAME:-$DEFAULT_DB_NAME}
Последняя информационная база 1С: ${LAST_IB_NAME:-$DEFAULT_IB_NAME}

ЛОГИНЫ И ПАРОЛИ:
ОС Linux root: пароль не хранится в скрипте, используется текущий root/sudo.
ОС Linux usr1cv8: служебный пользователь 1С, интерактивный пароль не задаётся.
PostgreSQL postgres: системный пользователь, локальный вход обычно через peer/sudo -u postgres.
PostgreSQL ${DEFAULT_DB_USER}: ${DEFAULT_DB_PASS}
PostgreSQL последний пользователь: ${LAST_DB_USER:-$DEFAULT_DB_USER}
PostgreSQL последний пароль: ${LAST_DB_PASS:-$DEFAULT_DB_PASS}
1С информационная база: ${LAST_IB_NAME:-$DEFAULT_IB_NAME}
1С пользователь информационной базы: не создаётся скриптом; для новой пустой базы обычно пользователь не задан.
Apache: логин/пароль не задаются; публикация открывается через модуль 1С.
License-tools: отдельный логин/пароль не задаётся скриптом.
Файл последних параметров: ${CREDENTIALS_FILE}

Apache:
Публикация по умолчанию: http://$(get_current_ip)/1c/${DEFAULT_IB_NAME}/
Дополнительный адрес маленькими буквами, если создан: http://$(get_current_ip)/1c/$(echo "${DEFAULT_IB_NAME}" | tr '[:upper:]' '[:lower:]')/

ЛИЦЕНЗИИ:
Каталог лицензий: /var/1C/licenses
Каталог настроек: /home/usr1cv8/.1cv8/1C/1cv8/conf
License-tools: /opt/1C/license-tools

ПОРТЫ:
5432 PostgreSQL
1540 1C ragent
1541 1C rmngr
1545 RAS
80/443 Apache

ПОЛЕЗНЫЕ ССЫЛКИ:
1. Дистрибутивы платформы 1С 8.3:
   https://releases.1c.ru/project/Platform83?allUpdates=true#updates
2. Postgres Pro для 1С:
   https://repo.postgrespro.ru/1c/
3. PostgreSQL для 1С / совместимость и материалы 1С:
   https://v8.1c.ru/tekhnologii/postgrespro/

ПОЛЕЗНЫЕ КОМАНДЫ:
systemctl status 1c-ragent --no-pager -l
systemctl status ras83 --no-pager -l
systemctl status ${PG_SERVICE} --no-pager -l
systemctl status apache2 --no-pager -l
/opt/1C/v8.3/x86_64/rac cluster list localhost:1545
============================================================
EOF2
  echo "Отчёт создан: $REPORT_FILE"
}

install_only_1c() {
  install_base_packages
  ensure_usr1cv8
  select_1c_archive
  extract_archive
  install_license_tools_from_unpack
  install_1c_debs_from_unpack
  configure_1c_services
  write_report
}

install_1c_apache_publication() {
  install_only_1c
  create_or_register_infobase_current_cluster
  publish_infobase_apache
  final_check
}

full_install() {
  install_base_packages
  ensure_usr1cv8
  install_postgresql_1c
  install_only_1c
  create_or_register_infobase_current_cluster
  publish_infobase_apache
  final_check
}

install_postgresql_1c_with_report() {
  install_postgresql_1c
  write_report
}

useful_links() {
  print_header "Полезные ссылки"
  echo "1. Дистрибутивы платформы 1С 8.3:"
  echo "   https://releases.1c.ru/project/Platform83?allUpdates=true#updates"
  echo
  echo "2. HASP/ETERSoft для Ubuntu:"
  echo "   https://download.etersoft.ru/pub/Etersoft/HASP/last/Ubuntu/22.04/"
  echo
  echo "3. Инструкция RARUS по установке 1С Linux:"
  echo "   https://rarus.ru/publications/20210927-ot-ekspertov-ustanovka-1c-linux-496320/#ustanovka-i-nastrojka-servera-1c"
  echo
}

main_menu() {
  while true; do
    clear || true
    echo "============================================================"
    echo "УНИВЕРСАЛЬНЫЙ УСТАНОВЩИК 1С ДЛЯ UBUNTU 24.04 (${SCRIPT_VERSION})"
    echo "============================================================"
    echo "Текущий каталог: $RUN_DIR"
    echo "Лог: $LOG_FILE"
    echo
    echo "1) Полная установка: 1С + PostgreSQL для 1С + Apache + публикация"
    echo "2) Установка 1С + Apache + публикация (PostgreSQL отдельно)"
    echo "3) Установка только 1С"
    echo "4) Установка только PostgreSQL для 1С"
    echo "5) Установка только Apache"
    echo "6) Публикация информационной базы 1С в Apache"
    echo "7) Удалить 1С"
    echo "8) Полное удаление PostgreSQL для 1С (требует 777)"
    echo "9) Удалить всё: 1С + PostgreSQL + Apache (требует 777)"
    echo "10) Финальная проверка"
    echo "11) Проверка лицензии/HASP"
    echo "12) Проверка license-tools"
    echo "13) Создать/зарегистрировать информационную базу в текущем активном кластере"
    echo "14) Проверить XML/VRD публикацию Apache"
    echo "15) Полезные ссылки"
    echo "0) Выход"
    echo
    read -r -p "Выберите пункт: " choice

    echo
    echo "Запуск пункта: $choice"
    echo "Лог: $LOG_FILE"
    echo

    set +e
    case "$choice" in
      1) full_install ;;
      2) install_1c_apache_publication ;;
      3) install_only_1c ;;
      4) install_postgresql_1c_with_report ;;
      5) install_apache_only ;;
      6) publish_infobase_apache ;;
      7) remove_1c ;;
      8) confirm_777 "полное удаление PostgreSQL для 1С" && remove_pg ;;
      9) confirm_777 "удаление всего: 1С + PostgreSQL + Apache" && remove_all ;;
      10) final_check ;;
      11) license_check ;;
      12) license_tools_check ;;
      13) create_or_register_infobase_current_cluster ;;
      14) check_publication_xml_vrd ;;
      15) useful_links ;;
      0) echo "Выход."; exit 0 ;;
      *) echo "Неверный пункт меню." ;;
    esac
    rc=$?
    set -e

    echo
    if [[ $rc -ne 0 ]]; then
      echo "Пункт завершился с ошибкой. Код: $rc"
      echo "Смотрите лог: $LOG_FILE"
    else
      echo "Пункт завершён."
    fi
    pause_enter
  done
}

require_root
main_menu
