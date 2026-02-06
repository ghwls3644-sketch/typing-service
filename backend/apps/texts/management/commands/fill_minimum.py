"""
부족한 카테고리 콘텐츠 채우기
Usage: python manage.py fill_minimum
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import uuid


# 한글 단어 고급 (6글자 이상) - 15개 추가
KO_WORDS_ADVANCED = [
    '프레젠테이션', '커뮤니케이션', '마케팅전략', '비즈니스모델', '스타트업창업',
    '고객서비스센터', '온라인마케팅', '모바일앱개발', '웹사이트디자인', '사용자경험설계',
    '정보보호시스템', '네트워크보안', '클라우드컴퓨팅', '서버관리자', '데이터분석가',
    '인공지능개발', '자동화시스템', '스마트홈시스템', '전자상거래플랫폼', '핀테크서비스',
]

# 한글 속담 중급 (19-30자) - 15개 추가
KO_PROVERBS_MEDIUM = [
    '하룻강아지 범 무서운 줄 모른다',
    '금강산도 식후경',
    '첫술에 배부르랴',
    '돼지에 진주 목걸이',
    '말이 씨가 된다',
    '장님 코끼리 만지기',
    '모로 가도 서울만 가면 된다',
    '물에 빠진 놈 건져 놓으니 보따리 내놓으라 한다',
    '같은 값이면 다홍치마',
    '원님 덕에 나팔 분다',
    '빛 좋은 개살구',
    '우는 아이 젖 준다',
    '등잔 밑이 어둡다',
    '무쇠도 갈면 바늘 된다',
    '땅 짚고 헤엄치기',
]

# 한글 속담 고급 (31-60자) - 25개 추가
KO_PROVERBS_ADVANCED = [
    '가랑비에 옷 젖는 줄 모르고 세월에 늙는 줄 모른다',
    '강물도 쓰면 줄고 쇠도 갈면 닳는다',
    '개 꼬리 삼 년 두어도 황모 되지 못한다',
    '구렁이 담 넘어가듯 한다',
    '길고 짧은 것은 대어 보아야 안다',
    '나무는 보고 숲은 보지 못한다',
    '낮말은 새가 듣고 밤말은 쥐가 듣는다',
    '눈에서 콩깍지가 벗겨지다',
    '닭 잡아먹고 오리발 내민다',
    '도둑이 제 발 저린다',
    '돌다리도 두들겨 보고 건너라',
    '등잔 밑이 어두운 줄 모른다',
    '뛰어야 벼룩이요 기어야 거미다',
    '말은 할수록 늘고 되는 될수록 준다',
    '발 없는 말이 천 리를 간다',
    '배부른 흥정이 없다',
    '백 번 듣는 것이 한 번 보는 것만 못하다',
    '뿔 빠진 송아지 울타리 바깥 나가듯',
    '사촌이 땅을 사면 배가 아프다',
    '서당 개 삼 년에 풍월을 읊는다',
    '식은 죽 먹기보다 더 쉽다',
    '악수는 악수를 낳는다',
    '양반은 얼어 죽어도 겉불은 안 쬔다',
    '열 번 찍어 안 넘어가는 나무 없다',
    '원숭이도 나무에서 떨어질 때가 있다',
]

# 영어 속담 중급 (41-75자) - 15개 추가
EN_PROVERBS_MEDIUM = [
    "Do not count your chickens before they hatch",
    "Every dog has its day and every man his hour",
    "Good things come to those who wait patiently",
    "It takes two to make a quarrel last longer",
    "Necessity is the mother of all invention",
    "One bad apple spoils the whole barrel",
    "Out of sight out of mind they say",
    "The early bird catches the worm indeed",
    "There are many fish in the sea to catch",
    "Time and tide wait for no man at all",
    "Too many cooks spoil the broth together",
    "What goes around comes around eventually",
    "Where there is smoke there is fire burning",
    "You reap what you sow in this life",
    "Beauty is in the eye of the beholder always",
]

# 영어 속담 고급 (76-120자) - 20개 추가
EN_PROVERBS_ADVANCED = [
    "A chain is only as strong as its weakest link in the entire chain system",
    "A fool and his money are soon parted as they say in the old days",
    "Actions speak louder than words but words can also hurt people deeply",
    "All good things must come to an end eventually no matter how hard we try",
    "An ounce of prevention is worth a pound of cure when dealing with problems",
    "Curiosity killed the cat but satisfaction brought it back to life again",
    "Do not bite the hand that feeds you because you may need it again someday",
    "Do not cry over spilled milk because what is done cannot be undone anymore",
    "Every cloud has a silver lining if you look hard enough to find it there",
    "Fools rush in where angels fear to tread and often get hurt in the process",
    "He who hesitates is lost but he who rushes may also make terrible mistakes",
    "If the mountain will not come to Muhammad then Muhammad must go to the mountain",
    "If you cannot beat them then you should consider joining them instead today",
    "It is better to be safe than sorry so always take precautions when possible",
    "Keep your friends close and your enemies even closer as the old saying goes",
    "Laughter is the best medicine for the soul and it costs nothing at all",
    "Let sleeping dogs lie because waking them up might cause unnecessary trouble",
    "Measure twice and cut once to avoid making costly mistakes in your work",
    "Never put off until tomorrow what you can do today if you have the time",
    "The road to hell is paved with good intentions as we often find out later",
]


class Command(BaseCommand):
    help = '부족한 카테고리에 최소 20개 콘텐츠를 채웁니다.'

    def handle(self, *args, **options):
        batch_id = f'fill-minimum-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 부족 카테고리 콘텐츠 채우기 시작... (batch_id: {batch_id})')
        
        results = {}
        
        # 1. 한글 단어 고급
        pack = TextPack.objects.filter(code='ko-word-daily-3').first()
        if pack:
            count = self._import_items(pack, KO_WORDS_ADVANCED, 'ko', batch_id)
            results['ko-word-daily-3'] = count
        
        # 2. 한글 속담 중급
        pack = TextPack.objects.filter(code='ko-short-proverb-2').first()
        if pack:
            count = self._import_items(pack, KO_PROVERBS_MEDIUM, 'ko', batch_id)
            results['ko-short-proverb-2'] = count
        
        # 3. 한글 속담 고급
        pack = TextPack.objects.filter(code='ko-short-proverb-3').first()
        if pack:
            count = self._import_items(pack, KO_PROVERBS_ADVANCED, 'ko', batch_id)
            results['ko-short-proverb-3'] = count
        
        # 4. 영어 속담 중급
        pack = TextPack.objects.filter(code='en-short-proverb-2').first()
        if pack:
            count = self._import_items(pack, EN_PROVERBS_MEDIUM, 'en', batch_id)
            results['en-short-proverb-2'] = count
        
        # 5. 영어 속담 고급
        pack = TextPack.objects.filter(code='en-short-proverb-3').first()
        if pack:
            count = self._import_items(pack, EN_PROVERBS_ADVANCED, 'en', batch_id)
            results['en-short-proverb-3'] = count
        
        self.stdout.write('\n📊 결과:')
        for code, count in results.items():
            self.stdout.write(f'  - {code}: +{count}개')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
    
    def _import_items(self, pack, items, lang, batch_id):
        count = 0
        for text in items:
            text = text.strip()
            normalized = TextItem.normalize_text(text, lang)
            
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=text,
                normalized_content=normalized,
                source_name='fill_minimum',
                import_batch_id=batch_id,
            )
            count += 1
        return count
