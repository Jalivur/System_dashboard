# Script: migrate_to_logging.sh
#!/bin/bash

# Reemplazar prints por logging
find . -name "*.py" -type f -exec sed -i 's/print(f"\[/logger.info("/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/print("Error/logger.error("/g' {} \;