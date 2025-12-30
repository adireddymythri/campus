
import os
import re

file_path = r'c:\Users\nagam\OneDrive\Desktop\campus_mart\campusmart\marketplace\templates\user_details.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Generic fix for any {{ ... }} with newlines
fixed_content = re.sub(r'\{\{\s*([a-zA-Z0-9_.\'\"|:\s]+)\s*\n\s*\}\}', r'{{\1}}', content)
fixed_content = re.sub(r'\{\{\s*\n\s*([a-zA-Z0-9_.\'\"|:\s]+)\s*\}\}', r'{{\1}}', fixed_content)

# Specific pattern fixes for the ones observed
fixed_content = fixed_content.replace('{{ user.phone_number|default:"No Phone"\n                        }}', '{{ user.phone_number|default:"No Phone" }}')
fixed_content = fixed_content.replace('{{ user.college_name|default:"College\n                        Not Set" }}', '{{ user.college_name|default:"College Not Set" }}')
fixed_content = fixed_content.replace('{{ user.college_id|default:"---"\n                        }}', '{{ user.college_id|default:"---" }}')
fixed_content = fixed_content.replace('{{ user.branch|default:"Branch" }}\n                    ', '{{ user.branch|default:"Branch" }}')
fixed_content = fixed_content.replace('{{ user.hostel_block|default:"Block" }}\n                        - {{ user.room_no|default:"Rm" }}', '{{ user.hostel_block|default:"Block" }} - {{ user.room_no|default:"Rm" }}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"File updated: {file_path}")
