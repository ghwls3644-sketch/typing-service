"""
v4.0 팩에 TextItem 데이터 추가 시드 커맨드
Usage: python manage.py seed_v4_items
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem


# 팩 코드별 아이템 데이터
PACK_ITEMS = {
    'ko-word-daily-1': [
        '안녕', '사랑', '행복', '자유', '희망', '꿈', '별', '달', '해', '하늘',
        '바다', '산', '강', '나무', '꽃', '새', '집', '책', '친구', '가족'
    ],
    'ko-word-daily-2': [
        '프로그램', '컴퓨터', '인터넷', '키보드', '모니터', '마우스', '타자연습',
        '개발자', '디자이너', '프로젝트', '데이터', '알고리즘', '소프트웨어'
    ],
    'ko-word-daily-3': [
        '인공지능', '머신러닝', '딥러닝', '블록체인', '클라우드', '빅데이터',
        '사이버보안', '프로그래밍', '데이터베이스', '자동화시스템'
    ],
    'en-word-daily-1': [
        'code', 'data', 'web', 'app', 'file', 'text', 'chat', 'user', 'link', 'page',
        'key', 'log', 'run', 'test', 'save', 'load', 'help', 'home', 'work', 'play'
    ],
    'en-word-daily-2': [
        'program', 'develop', 'project', 'keyboard', 'monitor', 'software',
        'website', 'browser', 'network', 'backend', 'frontend', 'database'
    ],
    'en-word-daily-3': [
        'programming', 'development', 'application', 'architecture', 'infrastructure',
        'optimization', 'implementation', 'authentication', 'authorization'
    ],
    'ko-short-proverb-1': [
        '가는 말이 고와야 오는 말이 곱다.',
        '낮말은 새가 듣고 밤말은 쥐가 듣는다.',
        '하늘은 스스로 돕는 자를 돕는다.',
        '천 리 길도 한 걸음부터.',
        '백문이 불여일견.',
        '시작이 반이다.',
        '고생 끝에 낙이 온다.',
        '꿩 먹고 알 먹고.',
    ],
    'ko-short-proverb-2': [
        '세 살 버릇 여든까지 간다.',
        '호랑이도 제 말 하면 온다.',
        '빈 수레가 요란하다.',
        '가랑비에 옷 젖는 줄 모른다.',
        '등잔 밑이 어둡다.',
        '소 잃고 외양간 고친다.',
        '원숭이도 나무에서 떨어진다.',
    ],
    'ko-short-proverb-3': [
        '될 성 부른 나무는 떡잎부터 알아본다.',
        '공든 탑이 무너지랴.',
        '아니 땐 굴뚝에 연기 나랴.',
        '핑계 없는 무덤 없다.',
        '티끌 모아 태산.',
        '뛰는 놈 위에 나는 놈 있다.',
    ],
    'en-short-proverb-1': [
        'Practice makes perfect.',
        'No pain, no gain.',
        'Time is money.',
        'Actions speak louder.',
        'Keep calm and code on.',
        'Less is more.',
        'Just do it.',
    ],
    'en-short-proverb-2': [
        'The early bird catches the worm.',
        'Seeing is believing.',
        'Every cloud has a silver lining.',
        'Rome was not built in a day.',
        'When in Rome, do as the Romans do.',
        'The pen is mightier than the sword.',
    ],
    'en-short-proverb-3': [
        'The quick brown fox jumps over the lazy dog.',
        'A journey of a thousand miles begins with a single step.',
        'You can lead a horse to water but you cannot make it drink.',
        'The only thing we have to fear is fear itself.',
        'In the middle of difficulty lies opportunity.',
    ],
}


class Command(BaseCommand):
    help = 'v4.0 팩에 TextItem 데이터를 추가합니다.'

    def handle(self, *args, **options):
        self.stdout.write('📦 v4.0 팩 아이템 시드 시작...')
        
        total_created = 0
        
        for pack_code, items in PACK_ITEMS.items():
            try:
                pack = TextPack.objects.get(code=pack_code)
            except TextPack.DoesNotExist:
                self.stdout.write(f'  ⚠️ 팩 없음: {pack_code}')
                continue
            
            # 기존 아이템이 있으면 스킵
            if pack.items.exists():
                self.stdout.write(f'  ⏭️ 이미 아이템 있음: {pack_code} ({pack.items.count()}개)')
                continue
            
            # 아이템 추가
            for i, content in enumerate(items):
                TextItem.objects.create(
                    pack=pack,
                    content=content,
                    length=len(content.replace(' ', '')),
                    order=i
                )
            
            total_created += len(items)
            self.stdout.write(f'  ✅ {pack_code}: {len(items)}개 아이템 추가')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ 완료! 총 {total_created}개 아이템 생성'
        ))
