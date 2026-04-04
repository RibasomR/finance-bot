"""
Healthcheck script for Docker container.

Verifies bot is alive by checking Telegram API connectivity.
"""

import sys
import os
import httpx
from pathlib import Path


def check_telegram_api() -> bool:
    """
    Check if bot can connect to Telegram API.
    
    Makes a simple getMe request to verify bot token is valid
    and Telegram API is accessible.
    
    :return: True if connection successful, False otherwise
    """
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("ERROR: BOT_TOKEN not set", file=sys.stderr)
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    print("OK: Bot is alive and connected to Telegram")
                    return True
                else:
                    print(f"ERROR: Telegram API returned not ok: {data}", file=sys.stderr)
                    return False
            else:
                print(f"ERROR: HTTP {response.status_code}", file=sys.stderr)
                return False
                
    except httpx.TimeoutException:
        print("ERROR: Timeout connecting to Telegram API", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return False


def check_log_freshness() -> bool:
    """
    Check if log file was updated recently (within last 5 minutes).
    
    This is a secondary check to ensure bot process is active.
    
    :return: True if log is fresh, False otherwise
    """
    log_path = Path("/app/logs/bot.log")
    
    if not log_path.exists():
        print("WARNING: Log file not found", file=sys.stderr)
        return True  ## Don't fail on missing log, bot might be starting
    
    try:
        import time
        mtime = log_path.stat().st_mtime
        age_seconds = time.time() - mtime
        
        ## Log should be updated within 5 minutes
        if age_seconds > 300:
            print(f"WARNING: Log file is {age_seconds:.0f}s old", file=sys.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"WARNING: Cannot check log freshness: {e}", file=sys.stderr)
        return True  ## Don't fail on check errors


def main() -> int:
    """
    Main healthcheck function.
    
    Performs multiple checks to verify bot health:
    1. Telegram API connectivity (critical)
    2. Log file freshness (warning only)
    
    :return: 0 if healthy, 1 if unhealthy
    """
    ## Critical check: Telegram API
    if not check_telegram_api():
        return 1
    
    ## Secondary check: Log freshness (warning only, doesn't fail healthcheck)
    check_log_freshness()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

