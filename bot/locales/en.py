"""
English localization for the bot.

Contains all UI strings in English.
"""

STRINGS = {
    # === General ===
    "language_changed": "Language changed!",
    "select_language": "Please select your language:",
    "error_generic": "An unexpected error occurred. Please try again later.",
    "error_data": "Invalid data: {error}",
    "error_db": "Database error. Please try again later or contact support.",
    "error_telegram_api": "Telegram communication error. Please try later.",
    "error_bad_request": "Invalid request. Please try again.",
    "error_auth": "Bot authorization error. Please contact the administrator.",
    "error_db_fallback": "The database is temporarily unavailable.\nPlease try again later or contact support.",
    "error_voice_fallback": "Voice recognition service is temporarily unavailable.\nUse manual input: /add",
    "cancel": "Cancel",
    "back": "Back",
    "confirm": "Confirm",
    "yes_delete": "Yes, delete",
    "skip": "Skip",
    "edit": "Edit",
    "create": "Create",

    # === Bot commands (BotCommand descriptions) ===
    "cmd_start": "Start the bot",
    "cmd_menu": "Main menu",
    "cmd_add": "Add transaction",
    "cmd_transactions": "All transactions",
    "cmd_stats": "Statistics",
    "cmd_help": "Help",

    # === Reply keyboard ===
    "btn_income": "Income",
    "btn_expense": "Expenses",
    "btn_stats": "Statistics",
    "btn_add": "Add",
    "btn_more": "More",
    "btn_all_transactions": "All transactions",
    "btn_by_period": "By period",
    "btn_categories": "Categories",
    "btn_export": "Export",
    "btn_settings": "Settings",
    "btn_back": "Back",

    # === /start ===
    "welcome": (
        "Hi, {name}!\n\n"
        "I'll help you track your income and expenses.\n\n"
        "<b>What I can do:</b>\n"
        "- Record transactions by voice\n"
        "- Add operations manually\n"
        "- Show statistics and analytics\n"
        "- Keep history of all operations\n"
        "- Export data to Excel\n\n"
        "Use the menu below for quick access to all features"
    ),

    # === /help ===
    "help_title": "Bot Help",
    "help_text": (
        "<b>Adding transactions:</b>\n"
        "- Send a voice message\n"
        '  Example: <i>"Spent 20 dollars on groceries"</i>\n\n'
        "- <b>Add</b> button in the menu\n"
        "  Step-by-step input with category selection\n\n"
        "<b>Viewing data:</b>\n"
        "- <b>Income</b> -- list of all income\n"
        "- <b>Expenses</b> -- list of all expenses\n"
        "- <b>Statistics</b> -- balance and analytics\n\n"
        "<b>Additional:</b>\n"
        "The <b>More</b> button opens:\n"
        "- All transactions\n"
        "- Filter by period\n"
        "- Category management\n"
        "- Export to Excel\n"
        "- Settings\n\n"
        "<b>Editing:</b>\n"
        "In the income/expense lists, tap a transaction button "
        "to change the amount, category, or delete it.\n\n"
        "<b>Tip:</b> Use the menu at the bottom of the screen for quick access!"
    ),

    # === Additional menu ===
    "additional_menu_title": "Additional features",
    "additional_menu_subtitle": "Choose a section:",

    # === Main menu ===
    "main_menu_title": "Main menu",
    "main_menu_subtitle": "Use the buttons below for quick access",
    "main_menu_action": "Choose an action:",

    # === Inline main menu buttons ===
    "menu_stats": "Statistics",
    "menu_all_transactions": "All transactions",
    "menu_income": "Income",
    "menu_expense": "Expenses",
    "menu_period": "By period",
    "menu_categories": "Categories",
    "menu_export": "Export",
    "menu_settings": "Settings",
    "menu_home": "Main menu",
    "menu_back": "Back to menu",

    # === Transactions ===
    "tx_add_title": "Add transaction",
    "tx_choose_type": "Choose the operation type:",
    "tx_type_income": "Income",
    "tx_type_expense": "Expense",
    "tx_enter_amount": "Enter the amount (numbers only):",
    "tx_amount_examples": "Examples: 500, 1500.50, 15000",
    "tx_amount_set": "Amount: {amount} {currency}",
    "tx_choose_category": "Choose a {type} category:",
    "tx_category_of_expense": "expense",
    "tx_category_of_income": "income",
    "tx_custom_category": "Other",
    "tx_custom_category_title": "Custom category",
    "tx_custom_category_prompt": "Enter the {type} category name:",
    "tx_category_set": "Category: {name}",
    "tx_enter_description": "Enter a description (optional):",
    "tx_confirmation_title": "Transaction confirmation",
    "tx_confirm_correct": "Is everything correct?",
    "tx_saved": "Transaction saved!",
    "tx_cancelled": "Transaction cancelled.",
    "tx_operation_cancelled": "Operation cancelled.",
    "tx_added": "Transaction added",
    "tx_amount_label": "Amount",
    "tx_category_label": "Category",
    "tx_description_label": "Description",
    "tx_error_save": "An error occurred while saving the transaction. Please try again.",
    "tx_error_not_enough_params": "Not enough parameters.\n\nUse format: <code>/add type amount [category] [description]</code>\nExample: <code>/add expense 500 groceries</code>",
    "tx_error_unknown_type": "Unknown operation type.\n\nUse: <b>income</b> or <b>expense</b>",
    "tx_error_invalid_amount": "Invalid amount.\n\nEnter a positive number.\nExamples: 500, 1500.50, 15000",
    "tx_error_no_category": "Could not determine the category.\n\nTry using step-by-step input: /add",
    "tx_error_enter_valid": "Enter a valid number:",

    # === Quick add type keywords ===
    "quick_expense_words": ["expense", "expenses", "spent", "spending"],
    "quick_income_words": ["income", "earnings", "salary", "earned"],

    # === Limits ===
    "limit_warning_transaction": (
        "<b>Warning!</b>\n\n"
        "The amount {amount}$ exceeds the transaction limit ({limit}$).\n\n"
        "Are you sure? You can continue or change the amount."
    ),
    "limit_warning_monthly_exceeded": (
        "<b>Monthly limit exceeded!</b>\n\n"
        "Spent this month: {spent}$\n"
        "Monthly limit: {limit}$\n"
        "Remaining: {remaining}$\n\n"
        "This transaction will exceed the limit by {over}$"
    ),
    "limit_warning_monthly_approaching": (
        "<b>Approaching the limit</b>\n\n"
        "After this transaction you'll spend {percent:.0f}% of the monthly limit.\n"
        "Remaining: {remaining}$"
    ),

    # === View transactions ===
    "view_income_title": "Income",
    "view_expense_title": "Expenses",
    "view_all_title": "All transactions",
    "view_page": "Page {page} of {total}",
    "view_tap_to_edit": "Tap a transaction to edit it",
    "view_no_transactions": "No transactions found",
    "view_no_income": "You have no income yet.",
    "view_no_expense": "You have no expenses yet.",
    "view_no_any": "You have no transactions yet.\n\nAdd your first transaction with /add",
    "view_nav_prev": "Back",
    "view_nav_next": "Next",

    # === Edit transaction ===
    "edit_title": "Edit transaction",
    "edit_what_change": "What would you like to change?",
    "edit_amount_title": "Edit amount",
    "edit_amount_current": "Current amount: <b>{amount} {currency}</b>",
    "edit_amount_enter": "Enter the new amount:",
    "edit_amount_updated": "Amount updated",
    "edit_amount_new": "New amount: <b>{amount} {currency}</b>",
    "edit_category_title": "Edit category",
    "edit_category_current": "Current category: {emoji} <b>{name}</b>",
    "edit_category_choose": "Choose a new category:",
    "edit_category_updated": "Category updated",
    "edit_category_new": "New category: {emoji} <b>{name}</b>",
    "edit_description_title": "Edit description",
    "edit_description_current": "Current description: {desc}",
    "edit_description_enter": "Enter a new description:",
    "edit_description_updated": "Description updated",
    "edit_description_new": "New description: {desc}",
    "edit_description_removed": "Description removed",
    "edit_description_not_set": "<i>not set</i>",
    "edit_error": "Error updating the transaction.",
    "edit_cancelled": "Editing cancelled.",

    # === Delete transaction ===
    "delete_confirm_title": "Delete confirmation",
    "delete_confirm_question": "Delete this transaction?",
    "delete_success": "Transaction deleted",
    "delete_not_found": "Transaction not found or already deleted.",
    "delete_cancelled": "Deletion cancelled.",

    # === Edit/delete transaction buttons ===
    "btn_amount": "Amount",
    "btn_category": "Category",
    "btn_description": "Description",
    "btn_delete": "Delete",

    # === Statistics ===
    "stats_title": "Statistics {period}",
    "stats_period_all": "for all time",
    "stats_period_selected": "for the selected period",
    "stats_income": "Income:",
    "stats_no_income": "No income",
    "stats_expense": "Expenses:",
    "stats_no_expense": "No expenses",
    "stats_operations": "Operations: {count}",
    "stats_balance": "Balance:",
    "stats_top_categories": "Top expense categories:",

    # === Period filter ===
    "period_title": "Period filter",
    "period_choose": "Choose a period:",
    "period_today": "Today",
    "period_yesterday": "Yesterday",
    "period_week": "Week",
    "period_month": "Month",
    "period_year": "Year",
    "period_all": "All time",

    # === Export ===
    "export_title": "Export data to Excel",
    "export_choose_period": "Choose the export period:",
    "export_generating": "Generating report {period}...",
    "export_generating_wait": "This may take a few seconds.",
    "export_done": "Export complete",
    "export_report": "Transaction report {period}",
    "export_date": "Generated: {date}",
    "export_what_next": "What's next?",
    "export_error": "Error creating the report",
    "export_error_detail": "Please try again later or contact support.",
    "export_btn_today": "Today",
    "export_btn_yesterday": "Yesterday",
    "export_btn_week": "Week",
    "export_btn_month": "Month",
    "export_btn_year": "Year",
    "export_btn_all": "All time",
    "export_period_today": "today",
    "export_period_yesterday": "yesterday",
    "export_period_week": "for the week",
    "export_period_month": "for the month",
    "export_period_year": "for the year",
    "export_period_all": "for all time",

    # === Excel export ===
    "excel_title": "Transaction report",
    "excel_sheet": "Transactions",
    "excel_stats": "Statistics",
    "excel_balance": "Total balance:",
    "excel_income": "Income:",
    "excel_expense": "Expenses:",
    "excel_operations_count": "Number of operations:",
    "excel_header_date": "Date",
    "excel_header_time": "Time",
    "excel_header_type": "Type",
    "excel_header_amount": "Amount",
    "excel_header_category": "Category",
    "excel_header_description": "Description",
    "excel_type_income": "Income",
    "excel_type_expense": "Expense",
    "excel_period_from_to": "from {start} to {end}",
    "excel_period_from": "from {start}",
    "excel_period_to": "to {end}",
    "excel_period_all": "for all time",

    # === Settings ===
    "settings_title": "Profile settings",
    "settings_subtitle": (
        "Here you can set spending limits.\n\n"
        "<b>What does it do?</b>\n"
        "- Control over large expenses\n"
        "- Warnings when limits are exceeded\n"
        "- More conscious approach to finances"
    ),
    "settings_transaction_limit": "Transaction limit",
    "settings_monthly_limit": "Monthly spending limit",
    "settings_view_limits": "My current limits",
    "settings_language": "Language / Язык",
    "settings_cancel": "Action cancelled",

    # === Transaction limit ===
    "settings_tx_limit_title": "Transaction limit",
    "settings_tx_limit_prompt": (
        "Enter the maximum amount for a single transaction.\n\n"
        "You'll get a warning when trying to add a transaction exceeding this amount.\n\n"
        "<i>Example: 50000</i>"
    ),
    "settings_tx_limit_set": "Limit set!",
    "settings_tx_limit_set_detail": (
        "Maximum transaction amount: {limit}$\n\n"
        "Now you'll get a warning when trying to add a transaction exceeding this amount."
    ),
    "settings_tx_limit_removed": "Personal limit removed",
    "settings_tx_limit_removed_detail": "Now using the default limit: {limit}$",
    "settings_limit_positive": "Limit must be a positive number. Try again.",
    "settings_limit_too_big": "Value is too large. Try again.",
    "settings_limit_invalid": "Invalid value. Enter a number.\n\n<i>Example: {example}</i>",
    "settings_error_save": "Error saving settings",

    # === Monthly limit ===
    "settings_monthly_title": "Monthly spending limit",
    "settings_monthly_prompt": (
        "Enter the maximum monthly spending amount.\n\n"
        "The bot will track your expenses and warn you when approaching the limit.\n\n"
        "<i>Example: 100000</i>"
    ),
    "settings_monthly_set": "Monthly limit set!",
    "settings_monthly_set_detail": (
        "Maximum monthly spending: {limit}$\n\n"
        "The bot will track your expenses and notify you at 80% and 100% of the limit."
    ),
    "settings_monthly_removed": "Monthly limit removed",
    "settings_monthly_removed_detail": "The bot will no longer track monthly spending.",

    # === View limits ===
    "limits_title": "Your limits",
    "limits_tx_label": "Transaction limit:",
    "limits_tx_personal": "{limit}$ (personal)",
    "limits_tx_default": "{limit}$ (default)",
    "limits_monthly_label": "Monthly spending limit:",
    "limits_monthly_not_set": "Not set",
    "limits_spent_label": "Spent this month:",
    "limits_spent_detail": "{spent}$ of {limit}$ ({percent:.1f}%)",
    "limits_remaining": "Remaining: {remaining}$",
    "limits_exceeded": "Limit exceeded!",
    "limits_approaching": "Warning! You're approaching the limit.",
    "limits_hint": "Tap a button to change limits.",

    # === Settings inline buttons ===
    "settings_btn_remove_limit": "Remove limit",
    "settings_btn_change": "Change",

    # === Categories ===
    "cat_management_title": "Category management",
    "cat_management_subtitle": (
        "Here you can view your categories, "
        "create new ones and edit existing ones.\n\n"
        "<b>Tip:</b> Create categories for accurate expense tracking!"
    ),
    "cat_my_categories": "My categories",
    "cat_add": "Add category",
    "cat_title_list": "Your categories",
    "cat_custom_label": "Custom:",
    "cat_no_custom": "You have no custom categories yet",
    "cat_default_count": "Default categories: {count}",
    "cat_choose_to_edit": "Choose a category to edit",
    "cat_no_categories": "You have no categories yet",

    # === Add category ===
    "cat_add_title": "Add category",
    "cat_add_choose_type": "First, choose the category type:",
    "cat_add_type_income": "income",
    "cat_add_type_expense": "expense",
    "cat_add_name_prompt": "Enter the new category name:\n\n<i>Examples: Subscriptions, Hobbies, Education</i>",
    "cat_add_name_too_long": "Name is too long. Maximum 100 characters.\n\nTry again:",
    "cat_add_name_too_short": "Name is too short. Minimum 2 characters.\n\nTry again:",
    "cat_add_emoji_prompt": "Now enter an emoji for the category:\n\n<i>Examples: ... </i>\n\nYou can copy any emoji",
    "cat_add_confirm": "Confirm category creation",
    "cat_add_type_label": "Type:",
    "cat_add_name_label": "Name:",
    "cat_add_emoji_label": "Emoji:",
    "cat_add_confirm_question": "Is everything correct?",
    "cat_created": "Category created!",
    "cat_created_detail": "You can now use it when adding transactions.",
    "cat_create_error": "An error occurred while creating the category.\n\nPlease try again.",

    # === Edit category ===
    "cat_detail_type_income": "Income",
    "cat_detail_type_expense": "Expense",
    "cat_detail_status_default": "Default",
    "cat_detail_status_custom": "Custom",
    "cat_detail_transactions": "Transactions: {count}",
    "cat_detail_locked": "Default categories cannot be changed or deleted",
    "cat_detail_choose_action": "Choose an action:",
    "cat_edit_name_title": "Edit name",
    "cat_edit_name_current": "Current name: <b>{name}</b>",
    "cat_edit_name_prompt": "Enter a new name:",
    "cat_edit_name_error": "Name must be 2-100 characters.\n\nTry again:",
    "cat_edit_emoji_title": "Edit emoji",
    "cat_edit_emoji_current": "Current emoji: {emoji}",
    "cat_edit_emoji_prompt": "Enter a new emoji:",
    "cat_updated": "Category updated!",
    "cat_update_error": "Could not update the category",
    "cat_not_found": "Category not found",

    # === Delete category ===
    "cat_delete_title": "Delete category",
    "cat_delete_has_transactions": (
        "<b>Warning!</b> This category has transactions.\n"
        "Deleting the category will also delete all related transactions.\n\n"
        "Are you sure?"
    ),
    "cat_delete_confirm": "Are you sure you want to delete this category?",
    "cat_deleted": "Category deleted",
    "cat_deleted_detail": "The category and all related transactions have been deleted.",
    "cat_delete_error": "Could not delete the category",
    "cat_operation_cancelled": "Operation cancelled",
    "cat_cancelled_subtitle": "Choose another action:",

    # === Category inline buttons ===
    "cat_btn_edit_name": "Edit name",
    "cat_btn_edit_emoji": "Edit emoji",
    "cat_btn_delete": "Delete category",
    "cat_btn_locked": "Default category",
    "cat_btn_no_custom": "No custom categories",
    "cat_btn_show_default": "Default categories",

    # === Voice messages ===
    "voice_processing": "Processing voice message...",
    "voice_recognizing": "Recognizing speech...",
    "voice_analyzing": "Analyzing text...",
    "voice_recognized_title": "Recognized from voice",
    "voice_transaction_data": "Transaction data:",
    "voice_error_recognize": "Could not recognize a transaction.\n\nTry rephrasing or use /add",
    "voice_error_category": "Could not determine the category.\n\nTry using /add",
    "voice_error_transcription": "Could not recognize speech: {error}\n\nTry again or use /add",
    "voice_error_parsing": "Processing error: {error}\n\nTry again or use /add",
    "voice_error_generic": "An error occurred while processing the voice message.\n\nTry again or use /add",
    "voice_error_empty_file": "Error: downloaded file is empty",

    # === Voice transaction editing ===
    "voice_edit_title": "Edit transaction",
    "voice_edit_choose_field": "Choose a field to edit:",
    "voice_edit_amount_title": "Edit amount",
    "voice_edit_amount_prompt": "Enter the new amount (numbers only):",
    "voice_edit_amount_positive": "Amount must be positive.\n\nEnter a valid number:",
    "voice_edit_amount_too_big": "Amount is too large (maximum 10,000,000).\n\nEnter a valid number:",
    "voice_edit_amount_invalid": "Invalid amount format.\n\nEnter a number (decimals with a dot):\nExamples: 500, 1500.50",
    "voice_edit_category_title": "Edit category",
    "voice_edit_category_choose": "Choose a {type} category:",
    "voice_edit_description_title": "Edit description",
    "voice_edit_description_current": "<i>Current:</i> {desc}",
    "voice_edit_description_prompt": 'Enter a new description or send "-" to remove:',
    "voice_edit_description_too_long": "Description is too long (maximum 500 characters).\n\nEnter a description:",
    "voice_edit_description_too_long_edit": "Description is too long (maximum 500 characters).\n\nEnter a description:",

    # === Default categories (keys) ===
    "cat_groceries": "Groceries",
    "cat_home": "Home & Utilities",
    "cat_transport": "Transport",
    "cat_health": "Health",
    "cat_clothing": "Clothing",
    "cat_entertainment": "Entertainment",
    "cat_restaurants": "Restaurants & Cafes",
    "cat_communication": "Phone & Internet",
    "cat_pharmacy": "Pharmacy",
    "cat_other": "Other",
    "cat_salary": "Salary",
    "cat_freelance": "Freelance",
    "cat_gift": "Gift",
    "cat_investments": "Investments",

    # === AI prompt ===
    "ai_prompt": """Analyze the text and extract financial transaction information.
Return JSON with fields:
- type: "income" or "expense"
- amount: number (amount only, without currency)
- currency: "RUB" or "USD" (transaction currency)
- category: string (transaction category)
- description: string or null (additional description)

Expense categories: Groceries, Transport, Restaurants, Health, Home, Entertainment, Clothing, Other
Income categories: Salary, Freelance, Gift, Investments, Other

Currency recognition rules:
- "dollars", "bucks", "$", "usd" → USD
- "rubles", "rub", "₽" → RUB
- If currency is not specified → USD (default)

If something is missing - use null.
If "thousand" or "k" - multiply the amount by 1000.

Text: "{text}"

Return ONLY JSON, no additional text.""",

    "ai_whisper_language": "en",
    "ai_default_currency": "USD",
}
