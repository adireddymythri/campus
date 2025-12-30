
import os

file_path = r'c:\Users\nagam\OneDrive\Desktop\campus_mart\campusmart\marketplace\templates\dashboard_v2.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific split patterns
fixed_content = content.replace('{{ user.first_name\n                        }}', '{{ user.first_name }}')
fixed_content = fixed_content.replace("onclick=\"filterProducts(event,'{{ category.name|lower }}')\">{{ category.name\n                    }}</div>", "onclick=\"filterProducts(event,'{{ category.name|lower }}')\">{{ category.name }}</div>")
fixed_content = fixed_content.replace('class="category-label category-{{ product.category.name|lower }}">{{\n                                    product.category.name }}</span>', 'class="category-label category-{{ product.category.name|lower }}">{{ product.category.name }}</span>')
fixed_content = fixed_content.replace('status-{{ product.status }} status-badge">{{\n                                    product.get_status_display }}</span>', 'status-{{ product.status }} status-badge">{{ product.get_status_display }}</span>')

# Also generic fix for any {{ ... }} with newlines
import re
fixed_content = re.sub(r'\{\{\s*([a-zA-Z0-9_.]+)\s*\n\s*\}\}', r'{{\1}}', fixed_content) # Simple variable
fixed_content = re.sub(r'\{\{\s*\n\s*([a-zA-Z0-9_.]+)\s*\}\}', r'{{\1}}', fixed_content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("File updated successfully")
