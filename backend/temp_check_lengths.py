import os
import django
from django.db.models import Avg, Min, Max, Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.texts.models import TextItem

print('--- Length Stats per Pack ---')
stats = TextItem.objects.values('pack__code', 'pack__difficulty').annotate(
    avg=Avg('length'), 
    min=Min('length'), 
    max=Max('length'),
    count=Count('id')
).order_by('pack__code')

for s in stats:
    print(f'{s["pack__code"]} (Diff {s["pack__difficulty"]}): Count {s["count"]}, Avg {s["avg"]:.1f}, Range {s["min"]}-{s["max"]}')
