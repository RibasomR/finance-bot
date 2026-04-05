"""
Русская локализация бота.

Содержит все строки интерфейса на русском языке.
"""

STRINGS = {
    # === Общие ===
    "language_changed": "Язык изменен!",
    "select_language": "Please select your language:",
    "error_generic": "Произошла непредвиденная ошибка. Попробуй позже.",
    "error_data": "Некорректные данные: {error}",
    "error_db": "Ошибка базы данных. Попробуй позже или обратись к администратору.",
    "error_telegram_api": "Ошибка связи с Telegram. Попробуй позже.",
    "error_bad_request": "Некорректный запрос. Попробуй еще раз.",
    "error_auth": "Ошибка авторизации бота. Свяжись с администратором.",
    "error_db_fallback": "База данных временно недоступна.\nПожалуйста, попробуй позже или обратись к администратору.",
    "error_voice_fallback": "Сервис распознавания голоса временно недоступен.\nИспользуй ручной ввод транзакций: /add",
    "cancel": "Отмена",
    "back": "Назад",
    "confirm": "Подтвердить",
    "yes_delete": "Да, удалить",
    "skip": "Пропустить",
    "edit": "Редактировать",
    "create": "Создать",

    # === Команды бота (BotCommand descriptions) ===
    "cmd_start": "Запустить бота",
    "cmd_menu": "Главное меню",
    "cmd_add": "Добавить транзакцию",
    "cmd_transactions": "Все транзакции",
    "cmd_stats": "Статистика",
    "cmd_help": "Справка",

    # === Reply клавиатура ===
    "btn_income": "Доходы",
    "btn_expense": "Расходы",
    "btn_stats": "Статистика",
    "btn_add": "Добавить",
    "btn_more": "Ещё",
    "btn_all_transactions": "Все транзакции",
    "btn_by_period": "За период",
    "btn_categories": "Категории",
    "btn_export": "Экспорт",
    "btn_settings": "Настройки",
    "btn_back": "Назад",

    # === /start ===
    "welcome": (
        "Привет, {name}!\n\n"
        "Я помогу вести учет твоих доходов и расходов.\n\n"
        "<b>Что я умею:</b>\n"
        "- Записывать транзакции голосом\n"
        "- Добавлять операции вручную\n"
        "- Показывать статистику и аналитику\n"
        "- Вести историю всех операций\n"
        "- Экспортировать данные в Excel\n\n"
        "Используй меню ниже для быстрого доступа ко всем функциям"
    ),

    # === /help ===
    "help_title": "Справка по боту",
    "help_text": (
        "<b>Добавление транзакций:</b>\n"
        "- Отправь голосовое сообщение\n"
        '  Пример: <i>"Потратил 500 рублей на продукты"</i>\n\n'
        "- Кнопка <b>Добавить</b> в меню\n"
        "  Пошаговый ввод с выбором категорий\n\n"
        "<b>Просмотр данных:</b>\n"
        "- <b>Доходы</b> -- список всех доходов\n"
        "- <b>Расходы</b> -- список всех расходов\n"
        "- <b>Статистика</b> -- баланс и аналитика\n\n"
        "<b>Дополнительно:</b>\n"
        "Кнопка <b>Ещё</b> открывает:\n"
        "- Все транзакции\n"
        "- Фильтр по периоду\n"
        "- Управление категориями\n"
        "- Экспорт в Excel\n"
        "- Настройки\n\n"
        "<b>Редактирование:</b>\n"
        "В списках доходов/расходов нажми на кнопку транзакции, "
        "чтобы изменить сумму, категорию или удалить.\n\n"
        "<b>Совет:</b> Используй меню внизу экрана для быстрого доступа!"
    ),

    # === Дополнительное меню ===
    "additional_menu_title": "Дополнительные функции",
    "additional_menu_subtitle": "Выбери нужный раздел:",

    # === Главное меню ===
    "main_menu_title": "Главное меню",
    "main_menu_subtitle": "Используй кнопки ниже для быстрого доступа",
    "main_menu_action": "Выберите действие:",

    # === Inline кнопки главного меню ===
    "menu_stats": "Статистика",
    "menu_all_transactions": "Все транзакции",
    "menu_income": "Доходы",
    "menu_expense": "Расходы",
    "menu_period": "За период",
    "menu_categories": "Категории",
    "menu_export": "Экспорт",
    "menu_settings": "Настройки",
    "menu_home": "Главное меню",
    "menu_back": "Назад в меню",

    # === Транзакции ===
    "tx_add_title": "Добавление транзакции",
    "tx_choose_type": "Выберите тип операции:",
    "tx_type_income": "Доход",
    "tx_type_expense": "Расход",
    "tx_enter_amount": "Введите сумму (только число):",
    "tx_amount_examples": "Примеры: 500, 1500.50, 15000",
    "tx_amount_set": "Сумма: {amount} {currency}",
    "tx_choose_category": "Выберите категорию {type}:",
    "tx_category_of_expense": "расхода",
    "tx_category_of_income": "дохода",
    "tx_custom_category": "Другое",
    "tx_custom_category_title": "Своя категория",
    "tx_custom_category_prompt": "Введите название категории {type}:",
    "tx_category_set": "Категория: {name}",
    "tx_enter_description": "Введите описание транзакции (опционально):",
    "tx_confirmation_title": "Подтверждение транзакции",
    "tx_confirm_correct": "Всё верно?",
    "tx_saved": "Транзакция сохранена!",
    "tx_cancelled": "Транзакция отменена.",
    "tx_operation_cancelled": "Операция отменена.",
    "tx_added": "Транзакция добавлена",
    "tx_amount_label": "Сумма",
    "tx_category_label": "Категория",
    "tx_description_label": "Описание",
    "tx_error_save": "Произошла ошибка при сохранении транзакции. Попробуйте еще раз.",
    "tx_error_not_enough_params": "Недостаточно параметров.\n\nИспользуйте формат: <code>/add тип сумма [категория] [описание]</code>\nПример: <code>/add расход 500 продукты</code>",
    "tx_error_unknown_type": "Неизвестный тип операции.\n\nИспользуйте: <b>доход</b> или <b>расход</b>",
    "tx_error_invalid_amount": "Некорректная сумма.\n\nВведите положительное число.\nПримеры: 500, 1500.50, 15000",
    "tx_error_no_category": "Не удалось определить категорию.\n\nПопробуйте использовать пошаговый ввод: /add",
    "tx_error_enter_valid": "Введите корректное число:",

    # === Quick add type keywords ===
    "quick_expense_words": ["расход", "расходы", "трата", "траты", "expense"],
    "quick_income_words": ["доход", "доходы", "заработок", "income"],

    # === Лимиты ===
    "limit_warning_transaction": (
        "<b>Внимание!</b>\n\n"
        "Сумма {amount}₽ превышает установленный лимит одной транзакции ({limit}₽).\n\n"
        "Ты уверен? Можешь продолжить или изменить сумму."
    ),
    "limit_warning_monthly_exceeded": (
        "<b>Превышение месячного лимита!</b>\n\n"
        "Потрачено в этом месяце: {spent}₽\n"
        "Месячный лимит: {limit}₽\n"
        "Осталось: {remaining}₽\n\n"
        "Эта транзакция превысит лимит на {over}₽"
    ),
    "limit_warning_monthly_approaching": (
        "<b>Приближение к лимиту</b>\n\n"
        "После этой транзакции ты потратишь {percent:.0f}% месячного лимита.\n"
        "Останется: {remaining}₽"
    ),

    # === Просмотр транзакций ===
    "view_income_title": "Доходы",
    "view_expense_title": "Расходы",
    "view_all_title": "Все транзакции",
    "view_page": "Страница {page} из {total}",
    "view_tap_to_edit": "Нажми на транзакцию, чтобы изменить её",
    "view_no_transactions": "Транзакции не найдены",
    "view_no_income": "У вас пока нет доходов.",
    "view_no_expense": "У вас пока нет расходов.",
    "view_no_any": "У вас пока нет транзакций.\n\nДобавьте первую транзакцию командой /add",
    "view_nav_prev": "Назад",
    "view_nav_next": "Вперед",

    # === Редактирование транзакции ===
    "edit_title": "Редактирование транзакции",
    "edit_what_change": "Что хотите изменить?",
    "edit_amount_title": "Редактирование суммы",
    "edit_amount_current": "Текущая сумма: <b>{amount} {currency}</b>",
    "edit_amount_enter": "Введите новую сумму:",
    "edit_amount_updated": "Сумма обновлена",
    "edit_amount_new": "Новая сумма: <b>{amount} {currency}</b>",
    "edit_category_title": "Редактирование категории",
    "edit_category_current": "Текущая категория: {emoji} <b>{name}</b>",
    "edit_category_choose": "Выберите новую категорию:",
    "edit_category_updated": "Категория обновлена",
    "edit_category_new": "Новая категория: {emoji} <b>{name}</b>",
    "edit_description_title": "Редактирование описания",
    "edit_description_current": "Текущее описание: {desc}",
    "edit_description_enter": "Введите новое описание:",
    "edit_description_updated": "Описание обновлено",
    "edit_description_new": "Новое описание: {desc}",
    "edit_description_removed": "Описание удалено",
    "edit_description_not_set": "<i>не указано</i>",
    "edit_error": "Ошибка при обновлении транзакции.",
    "edit_cancelled": "Редактирование отменено.",

    # === Удаление транзакции ===
    "delete_confirm_title": "Подтверждение удаления",
    "delete_confirm_question": "Удалить эту транзакцию?",
    "delete_success": "Транзакция удалена",
    "delete_not_found": "Транзакция не найдена или уже удалена.",
    "delete_cancelled": "Удаление отменено.",

    # === Кнопки для редактирования/удаления транзакций ===
    "btn_amount": "Сумма",
    "btn_category": "Категория",
    "btn_description": "Описание",
    "btn_delete": "Удалить",

    # === Статистика ===
    "stats_title": "Статистика {period}",
    "stats_period_all": "за всё время",
    "stats_period_selected": "за выбранный период",
    "stats_income": "Доходы:",
    "stats_no_income": "Нет доходов",
    "stats_expense": "Расходы:",
    "stats_no_expense": "Нет расходов",
    "stats_operations": "Операций: {count}",
    "stats_balance": "Баланс:",
    "stats_top_categories": "Топ категорий расходов:",

    # === Фильтр по периоду ===
    "period_title": "Фильтр по периоду",
    "period_choose": "Выберите период:",
    "period_today": "Сегодня",
    "period_yesterday": "Вчера",
    "period_week": "Неделя",
    "period_month": "Месяц",
    "period_year": "Год",
    "period_all": "Всё время",

    # === Экспорт ===
    "export_title": "Экспорт данных в Excel",
    "export_choose_period": "Выберите период для экспорта транзакций:",
    "export_generating": "Генерирую отчет {period}...",
    "export_generating_wait": "Это может занять несколько секунд.",
    "export_done": "Экспорт завершен",
    "export_report": "Отчет по транзакциям {period}",
    "export_date": "Дата формирования: {date}",
    "export_what_next": "Что дальше?",
    "export_error": "Ошибка при создании отчета",
    "export_error_detail": "Попробуйте позже или обратитесь в поддержку.",
    "export_btn_today": "Сегодня",
    "export_btn_yesterday": "Вчера",
    "export_btn_week": "Неделя",
    "export_btn_month": "Месяц",
    "export_btn_year": "Год",
    "export_btn_all": "Всё время",
    "export_period_today": "сегодня",
    "export_period_yesterday": "вчера",
    "export_period_week": "за неделю",
    "export_period_month": "за месяц",
    "export_period_year": "за год",
    "export_period_all": "за всё время",

    # === Excel export ===
    "excel_title": "Отчет по транзакциям",
    "excel_sheet": "Транзакции",
    "excel_stats": "Статистика",
    "excel_balance": "Общий баланс:",
    "excel_income": "Доходы:",
    "excel_expense": "Расходы:",
    "excel_operations_count": "Количество операций:",
    "excel_header_date": "Дата",
    "excel_header_time": "Время",
    "excel_header_type": "Тип",
    "excel_header_amount": "Сумма",
    "excel_header_category": "Категория",
    "excel_header_description": "Описание",
    "excel_type_income": "Доход",
    "excel_type_expense": "Расход",
    "excel_period_from_to": "с {start} по {end}",
    "excel_period_from": "с {start}",
    "excel_period_to": "по {end}",
    "excel_period_all": "за всё время",

    # === Настройки ===
    "settings_title": "Настройки профиля",
    "settings_subtitle": (
        "Здесь ты можешь установить лимиты для контроля расходов.\n\n"
        "<b>Что это даёт?</b>\n"
        "- Контроль за крупными тратами\n"
        "- Предупреждения при превышении лимитов\n"
        "- Более осознанный подход к финансам"
    ),
    "settings_transaction_limit": "Лимит одной транзакции",
    "settings_monthly_limit": "Месячный лимит трат",
    "settings_view_limits": "Мои текущие лимиты",
    "settings_language": "Язык / Language",
    "settings_cancel": "Действие отменено",

    # === Лимит транзакции ===
    "settings_tx_limit_title": "Лимит одной транзакции",
    "settings_tx_limit_prompt": (
        "Введи максимальную сумму для одной транзакции в рублях.\n\n"
        "При попытке добавить транзакцию больше этой суммы ты получишь предупреждение.\n\n"
        "<i>Например: 50000</i>"
    ),
    "settings_tx_limit_set": "Лимит установлен!",
    "settings_tx_limit_set_detail": (
        "Максимальная сумма транзакции: {limit}₽\n\n"
        "Теперь при попытке добавить транзакцию больше этой суммы ты получишь предупреждение."
    ),
    "settings_tx_limit_removed": "Персональный лимит удален",
    "settings_tx_limit_removed_detail": "Теперь используется лимит по умолчанию: {limit}₽",
    "settings_limit_positive": "Лимит должен быть положительным числом. Попробуй еще раз.",
    "settings_limit_too_big": "Слишком большое значение. Попробуй еще раз.",
    "settings_limit_invalid": "Некорректное значение. Введи число в рублях.\n\n<i>Например: {example}</i>",
    "settings_error_save": "Ошибка сохранения настроек",

    # === Месячный лимит ===
    "settings_monthly_title": "Месячный лимит трат",
    "settings_monthly_prompt": (
        "Введи максимальную сумму расходов на месяц в рублях.\n\n"
        "Бот будет отслеживать твои траты и предупреждать при приближении к лимиту.\n\n"
        "<i>Например: 100000</i>"
    ),
    "settings_monthly_set": "Месячный лимит установлен!",
    "settings_monthly_set_detail": (
        "Максимальные траты в месяц: {limit}₽\n\n"
        "Бот будет отслеживать твои расходы и уведомлять при достижении 80% и 100% лимита."
    ),
    "settings_monthly_removed": "Месячный лимит удален",
    "settings_monthly_removed_detail": "Теперь бот не будет отслеживать месячные траты.",

    # === Просмотр лимитов ===
    "limits_title": "Твои лимиты",
    "limits_tx_label": "Лимит одной транзакции:",
    "limits_tx_personal": "{limit}₽ (персональный)",
    "limits_tx_default": "{limit}₽ (по умолчанию)",
    "limits_monthly_label": "Месячный лимит трат:",
    "limits_monthly_not_set": "Не установлен",
    "limits_spent_label": "Потрачено в этом месяце:",
    "limits_spent_detail": "{spent}₽ из {limit}₽ ({percent:.1f}%)",
    "limits_remaining": "Осталось: {remaining}₽",
    "limits_exceeded": "Лимит превышен!",
    "limits_approaching": "Внимание! Скоро достигнешь лимита.",
    "limits_hint": "Нажми на соответствующую кнопку, чтобы изменить лимиты.",

    # === Inline кнопки настроек ===
    "settings_btn_remove_limit": "Удалить лимит",
    "settings_btn_change": "Изменить",

    # === Категории ===
    "cat_management_title": "Управление категориями",
    "cat_management_subtitle": (
        "Здесь ты можешь просматривать свои категории, "
        "создавать новые и редактировать существующие.\n\n"
        "<b>Совет:</b> Создавай категории для точного учёта расходов!"
    ),
    "cat_my_categories": "Мои категории",
    "cat_add": "Добавить категорию",
    "cat_title_list": "Твои категории",
    "cat_custom_label": "Пользовательские:",
    "cat_no_custom": "У тебя пока нет пользовательских категорий",
    "cat_default_count": "Предустановленных категорий: {count}",
    "cat_choose_to_edit": "Выбери категорию для редактирования",
    "cat_no_categories": "У тебя пока нет категорий",

    # === Добавление категории ===
    "cat_add_title": "Добавление категории",
    "cat_add_choose_type": "Сначала выбери тип категории:",
    "cat_add_type_income": "доходов",
    "cat_add_type_expense": "расходов",
    "cat_add_name_prompt": "Введи название новой категории:\n\n<i>Например: Подписки, Хобби, Образование</i>",
    "cat_add_name_too_long": "Название слишком длинное. Максимум 100 символов.\n\nПопробуй еще раз:",
    "cat_add_name_too_short": "Название слишком короткое. Минимум 2 символа.\n\nПопробуй еще раз:",
    "cat_add_emoji_prompt": "Теперь введи эмодзи для категории:\n\n<i>Например: ... </i>\n\nМожешь скопировать любой эмодзи",
    "cat_add_confirm": "Подтверди создание категории",
    "cat_add_type_label": "Тип:",
    "cat_add_name_label": "Название:",
    "cat_add_emoji_label": "Эмодзи:",
    "cat_add_confirm_question": "Всё верно?",
    "cat_created": "Категория создана!",
    "cat_created_detail": "Теперь ты можешь использовать её при добавлении транзакций.",
    "cat_create_error": "Произошла ошибка при создании категории.\n\nПопробуй еще раз.",

    # === Редактирование категории ===
    "cat_detail_type_income": "Доход",
    "cat_detail_type_expense": "Расход",
    "cat_detail_status_default": "Предустановленная",
    "cat_detail_status_custom": "Пользовательская",
    "cat_detail_transactions": "Транзакций: {count}",
    "cat_detail_locked": "Предустановленные категории нельзя изменить или удалить",
    "cat_detail_choose_action": "Выбери действие:",
    "cat_edit_name_title": "Изменение названия",
    "cat_edit_name_current": "Текущее название: <b>{name}</b>",
    "cat_edit_name_prompt": "Введи новое название:",
    "cat_edit_name_error": "Название должно быть от 2 до 100 символов.\n\nПопробуй еще раз:",
    "cat_edit_emoji_title": "Изменение эмодзи",
    "cat_edit_emoji_current": "Текущий эмодзи: {emoji}",
    "cat_edit_emoji_prompt": "Введи новый эмодзи:",
    "cat_updated": "Категория обновлена!",
    "cat_update_error": "Не удалось обновить категорию",
    "cat_not_found": "Категория не найдена",

    # === Удаление категории ===
    "cat_delete_title": "Удаление категории",
    "cat_delete_has_transactions": (
        "<b>Внимание!</b> У этой категории есть транзакции.\n"
        "При удалении категории все связанные транзакции также будут удалены.\n\n"
        "Ты уверен?"
    ),
    "cat_delete_confirm": "Ты уверен, что хочешь удалить эту категорию?",
    "cat_deleted": "Категория удалена",
    "cat_deleted_detail": "Категория и все связанные с ней транзакции удалены.",
    "cat_delete_error": "Не удалось удалить категорию",
    "cat_operation_cancelled": "Операция отменена",
    "cat_cancelled_subtitle": "Выбери другое действие:",

    # === Inline кнопки категорий ===
    "cat_btn_edit_name": "Изменить название",
    "cat_btn_edit_emoji": "Изменить эмодзи",
    "cat_btn_delete": "Удалить категорию",
    "cat_btn_locked": "Предустановленная категория",
    "cat_btn_no_custom": "Нет пользовательских категорий",
    "cat_btn_show_default": "Предустановленные категории",

    # === Голосовые сообщения ===
    "voice_processing": "Обрабатываю голосовое сообщение...",
    "voice_recognizing": "Распознаю речь...",
    "voice_analyzing": "Анализирую текст...",
    "voice_recognized_title": "Распознано из голоса",
    "voice_transaction_data": "Данные транзакции:",
    "voice_error_recognize": "Не удалось распознать транзакцию.\n\nПопробуйте сформулировать по-другому или используйте /add",
    "voice_error_category": "Не удалось определить категорию.\n\nПопробуйте использовать команду /add",
    "voice_error_transcription": "Не удалось распознать речь: {error}\n\nПопробуйте еще раз или используйте /add",
    "voice_error_parsing": "Ошибка обработки: {error}\n\nПопробуйте еще раз или используйте /add",
    "voice_error_generic": "Произошла ошибка при обработке голосового сообщения.\n\nПопробуйте еще раз или используйте /add",
    "voice_error_empty_file": "Ошибка: скачанный файл пустой",

    # === Редактирование голосовой транзакции ===
    "voice_edit_title": "Редактирование транзакции",
    "voice_edit_choose_field": "Выберите поле для редактирования:",
    "voice_edit_amount_title": "Редактирование суммы",
    "voice_edit_amount_prompt": "Введите новую сумму (только число):",
    "voice_edit_amount_positive": "Сумма должна быть положительной.\n\nВведите корректное число:",
    "voice_edit_amount_too_big": "Сумма слишком большая (максимум 10 000 000).\n\nВведите корректное число:",
    "voice_edit_amount_invalid": "Некорректный формат суммы.\n\nВведите число (можно с копейками через точку):\nПримеры: 500, 1500.50",
    "voice_edit_category_title": "Редактирование категории",
    "voice_edit_category_choose": "Выберите категорию {type}:",
    "voice_edit_description_title": "Редактирование описания",
    "voice_edit_description_current": "<i>Текущее:</i> {desc}",
    "voice_edit_description_prompt": 'Введите новое описание или отправьте "-" чтобы удалить:',
    "voice_edit_description_too_long": "Описание слишком длинное (максимум 500 символов).\n\nВведите описание:",
    "voice_edit_description_too_long_edit": "Описание слишком длинное (максимум 500 символов).\n\nВведите описание:",

    # === Дефолтные категории (ключи) ===
    "cat_groceries": "Продукты",
    "cat_home": "Дом и ЖКХ",
    "cat_transport": "Транспорт",
    "cat_health": "Здоровье",
    "cat_clothing": "Одежда",
    "cat_entertainment": "Развлечения",
    "cat_restaurants": "Рестораны и кафе",
    "cat_communication": "Связь и интернет",
    "cat_pharmacy": "Аптека",
    "cat_other": "Другое",
    "cat_salary": "Зарплата",
    "cat_freelance": "Фриланс",
    "cat_gift": "Подарок",
    "cat_investments": "Инвестиции",

    # === AI промпт ===
    "ai_prompt": """Проанализируй текст и извлеки информацию о финансовой транзакции.
Верни JSON с полями:
- type: "income" или "expense"
- amount: число (только сумма, без валюты)
- currency: "RUB" или "USD" (валюта транзакции)
- category: строка (категория транзакции)
- description: строка или null (дополнительное описание)

Категории расходов: Продукты, Транспорт, Рестораны, Здоровье, Дом, Развлечения, Одежда, Другое
Категории доходов: Зарплата, Фриланс, Подарок, Инвестиции, Другое

Правила распознавания валюты:
- "рублей", "руб", "₽", "р" → RUB
- "долларов", "баксов", "долл", "$", "usd" → USD
- Если валюта не указана → RUB (по умолчанию)

Если чего-то нет - используй null.
Если "тысяч" или "тыс" - умножь сумму на 1000.

Текст: "{text}"

Верни ТОЛЬКО JSON, без дополнительного текста.""",

    "ai_whisper_language": "ru",
    "ai_default_currency": "RUB",
}
