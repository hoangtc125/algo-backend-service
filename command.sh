find . -type d \( -name "mongodb" -o -name "rabbitmq" -o -name "__pycache__" -o -name ".git" -o -name "2023" \) -prune -o -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g' > tree.txt
