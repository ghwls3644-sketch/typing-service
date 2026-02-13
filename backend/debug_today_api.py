import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from datetime import date
from rest_framework.test import APIRequestFactory
from apps.challenges.views import DailyChallengeViewSet
from apps.challenges.models import ClientChallenge, DailyChallenge

def debug_today_challenge(guest_id):
    print(f"--- Debugging for Guest ID: {guest_id} ---")
    
    # 1. Check Challenge
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).first()
    print(f"Today's Challenge: {challenge} (ID: {challenge.id if challenge else 'None'})")
    
    if not challenge:
        return

    # 2. Check ClientChallenge Record
    record = ClientChallenge.objects.filter(
        guest_session_id=guest_id, 
        challenge=challenge
    ).first()
    print(f"ClientChallenge Record: {record} (ID: {record.id if record else 'None'})")
    
    if record:
        print(f"  - Status: {record.status}")
        print(f"  - Current Sessions: {record.current_sessions}")
    
    # 3. Simulate View Request
    factory = APIRequestFactory()
    view = DailyChallengeViewSet.as_view({'get': 'today'})
    request = factory.get(f'/api/challenges/daily/today/?guest_session_id={guest_id}')
    
    response = view(request)
    print(f"API Response Status: {response.status_code}")
    data = response.data
    
    if 'my_progress' in data:
        print("✅ 'my_progress' found in response!")
        print(data['my_progress'])
    else:
        print("❌ 'my_progress' NOT found in response.")

if __name__ == "__main__":
    # Use the guest ID from your previous test: 'test-debug-123'
    debug_today_challenge('test-debug-123')
