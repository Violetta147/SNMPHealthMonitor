
import os
import re

TEMPLATE_DIR = r"c:\Users\LAPTOP T&T\.gemini\antigravity\playground\ionized-astro\template"

# Mappings: (regex_pattern, replacement)
replacements = [
    (r"url_for\('index'\)", "url_for('web.index')"),
    (r"url_for\('login'\)", "url_for('web.login')"),
    (r"url_for\('logout'\)", "url_for('web.logout')"),
    (r"url_for\('system'\)", "url_for('web.system')"),
    (r"url_for\('files'", "url_for('web.files'"),
    (r"url_for\('download'", "url_for('web.download'"),
    (r"url_for\('download_backup'", "url_for('web.download_backup'"),
    (r"url_for\('edit'", "url_for('web.edit'"),
    (r"url_for\('trash'\)", "url_for('web.trash')"),
    
    # API replacements - assuming names in api/router.py match functionality
    # api_check_exists -> api.check_exists
    (r"url_for\('api_check_exists'\)", "url_for('api.check_exists')"),
    (r"url_for\('api_upload_chunk'\)", "url_for('api.upload_chunk')"),
    (r"url_for\('api_delete'\)", "url_for('api.delete_item')"), # mapped to delete_item
    (r"url_for\('api_save'\)", "url_for('api.save')"),
    (r"url_for\('api_zip'\)", "url_for('api.zip_items')"), # mapped to zip_items
    (r"url_for\('api_unzip'\)", "url_for('api.unzip_item')"), # mapped to unzip_item
    (r"url_for\('api_delete_batch'\)", "url_for('api.delete_batch')"),
    (r"url_for\('api_trash_empty'\)", "url_for('api.trash_empty')"),
    (r"url_for\('api_backups'\)", "url_for('api.backups')"),
    (r"url_for\('api_restore_backup'\)", "url_for('api.restore_backup')"),
    (r"url_for\('api_backup_content'\)", "url_for('api.backup_content')"),
    (r"url_for\('api_restore'\)", "url_for('api.restore')"),
    (r"url_for\('api_delete_permanent'\)", "url_for('api.delete_permanent')"),
    
    # Just in case of quotes difference
    (r'url_for\("index"\)', "url_for('web.index')"),
    (r'url_for\("api_check_exists"\)', "url_for('api.check_exists')"),
    (r'url_for\("api_upload_chunk"\)', "url_for('api.upload_chunk')"),
    (r'url_for\("api_delete"\)', "url_for('api.delete_item')"),
    (r'url_for\("api_zip"\)', "url_for('api.zip_items')"),
    (r'url_for\("api_unzip"\)', "url_for('api.unzip_item')"),
]

for root, dirs, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for pattern, subst in replacements:
                content = re.sub(pattern, subst, content)
            
            if content != original_content:
                print(f"Updating {file}")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Template updates complete.")
