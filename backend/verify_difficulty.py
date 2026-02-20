import os
import django
import sys
from django.test import RequestFactory
from rest_framework.test import force_authenticate

# Setup Django
sys.path.append('/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.texts.views import TextItemViewSet
from apps.texts.models import TextItem

def test_difficulty(lang, mode, difficulty):
    factory = RequestFactory()
    url = f'/api/texts/items/practice_items/?language={lang}&mode={mode}&difficulty={difficulty}&count=20'
    request = factory.get(url)
    
    view = TextItemViewSet.as_view({'get': 'practice_items'})
    response = view(request)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
        
    data = response.data
    items = data.get('items', [])
    pack_code = data.get('pack_code')
    
    if not items:
        print(f"[{lang}-{mode}-Lv{difficulty}] No items found.")
        return

    lengths = [len(item.replace(' ', '')) for item in items]
    avg_len = sum(lengths) / len(lengths)
    min_len = min(lengths)
    max_len = max(lengths)
    
    print(f"[{lang}-{mode}-Lv{difficulty}] Code: {pack_code}, Count: {len(items)}, Avg Len: {avg_len:.1f}, Range: {min_len}-{max_len}")

print("--- Verifying Text Difficulty Logic ---")
print("\n[Korean Word]")
test_difficulty('ko', 'word', 1)
test_difficulty('ko', 'word', 2)
test_difficulty('ko', 'word', 3)

print("\n[Korean Short]")
test_difficulty('ko', 'short', 1)
test_difficulty('ko', 'short', 2)
test_difficulty('ko', 'short', 3)

print("\n[English Word]")
test_difficulty('en', 'word', 1)
test_difficulty('en', 'word', 2)
test_difficulty('en', 'word', 3)

print("\n[English Short]")
test_difficulty('en', 'short', 1)
test_difficulty('en', 'short', 2)
test_difficulty('en', 'short', 3)
