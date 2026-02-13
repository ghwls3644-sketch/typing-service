from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem

class Command(BaseCommand):
    help = '긴 문장/단어 데이터 추가 (난이도 3용)'

    def handle(self, *args, **options):
        # 1. Korean Short Level 3 Items (>= 19 chars excluding spaces)
        ko_short_l3_items = [
            '가루는 칠수록 고와지고 말은 할수록 거칠어진다.', # 19
            '개구리 올챙이 적 생각 못 하고 으스댄다.', # 17.. wait. 개구리올챙이적생각못하고으스댄다 (17) -> Need longer.
            '남의 눈에 눈물 내면 제 눈에는 피눈물이 난다.', # 18.. 
            '돌다리도 두들겨 보고 건너라는 옛말이 있다.', # 17..
            '모기는 작아도 온몸이 붓게 만들 수 있다.', # 16
            # Let's make sure they are definitely long enough
            '호랑이에게 물려가도 정신만 바짝 차리면 살 수 있다.', # 21 (호랑이에게물려가도정신만바짝차리면살수있다)
            '열 번 찍어 안 넘어가는 나무 없다는 말을 믿어라.', # 19 (열번찍어안넘어가는나무없다는말을믿어라 - 20?)
            '윗물이 맑아야 아랫물이 맑다는 것을 기억해라.', # 19 
            '지렁이도 밟으면 꿈틀한다는 것을 보여줘야 한다.', # 19
            '천 리 길도 한 걸음부터라는 말이 있듯이 시작해라.', # 20
            '티끌 모아 태산이 되려면 꾸준함이 가장 중요하다.', # 19
            '한 번 실수는 병가지상사가 아니라고 생각하면 안 된다.', # 21
            '세 살 버릇이 여든까지 간다는 말을 명심해야 한다.', # 20
            '웃는 얼굴에 침 뱉지 못한다는 말이 틀린 적 없다.', # 20
            '소 잃고 외양간 고치는 일이 없도록 미리 대비해라.', # 20
        ]

        # 2. Korean Word Level 3 Items (>= 7 chars)
        ko_word_l3_items = [
            '소프트웨어엔지니어링',
            '데이터베이스관리자',
            '객체지향프로그래밍',
            '하이퍼텍스트마크업',
            '캐스케이딩스타일시트',
            '자바스크립트개발자',
            '리액트네이티브앱',
            '아마존웹서비스',
            '구글클라우드플랫폼',
            '마이크로서비스아키텍처',
            '비동기프로그래밍',
            '인터페이스디자인',
            '사용자경험테스트',
            '가상머신인스턴스',
            '컨테이너오케스트레이션'
        ]

        # Add logic
        self.add_items('ko', 'short', 'proverb', 3, ko_short_l3_items)
        self.add_items('ko', 'word', 'daily', 3, ko_word_l3_items)

        self.stdout.write(self.style.SUCCESS('Successfully seeded long items.'))

    def add_items(self, lang, kind, theme, diff, items):
        pack = TextPack.objects.filter(
            language=lang, kind=kind, theme=theme, difficulty=diff
        ).first()

        if not pack:
            self.stdout.write(f'Pack not found for {lang}-{kind}-{diff}')
            return

        count = 0
        current_max_order = pack.items.order_by('-order').first()
        start_order = (current_max_order.order + 1) if current_max_order else 0

        for i, content in enumerate(items):
            # 중복 체크
            if pack.items.filter(content=content).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=content,
                length=len(content.replace(' ', '')),
                order=start_order + i
            )
            count += 1
        
        self.stdout.write(f'Added {count} items to {pack.code}')
