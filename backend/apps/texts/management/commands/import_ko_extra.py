"""
추가 한글 단어/속담 배치 import
Usage: python manage.py import_ko_extra
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import uuid


# 추가 한글 단어 (총 200+ 개)
EXTRA_KO_WORDS = [
    # 초급 (2-3글자) - 60개
    '사과', '바나나', '포도', '딸기', '수박', '참외', '복숭아', '귤', '배', '감',
    '연필', '지우개', '가위', '풀', '자', '공책', '책상', '의자', '창문', '문',
    '하늘', '바다', '구름', '비', '눈', '바람', '맑음', '흐림', '안개', '번개',
    '엄마', '아빠', '언니', '오빠', '동생', '할머니', '할아버지', '친구', '선생님', '학생',
    '사랑', '행복', '기쁨', '슬픔', '화남', '놀람', '웃음', '눈물', '마음', '희망',
    '아침', '점심', '저녁', '오늘', '내일', '어제', '지금', '나중', '항상', '가끔',
    
    # 중급 (4-5글자) - 60개
    '컴퓨터', '키보드', '마우스', '모니터', '스피커', '프린터', '스캐너', '태블릿', '스마트폰', '노트북',
    '인터넷', '와이파이', '블루투스', '케이블', '어댑터', '충전기', '배터리', '화면보호', '데이터', '클라우드',
    '가족사진', '졸업앨범', '생일파티', '크리스마스', '설날', '추석', '어린이날', '어버이날', '스승의날', '한글날',
    '자동차', '오토바이', '자전거', '버스', '지하철', '기차', '비행기', '배', '택시', '트럭',
    '아파트', '빌라', '단독주택', '오피스텔', '원룸', '투룸', '쓰리룸', '거실', '침실', '욕실',
    '냉장고', '세탁기', '에어컨', '히터', '청소기', '전자레인지', '밥솥', '가스레인지', '오븐', '토스터',
    
    # 고급 (6글자 이상) - 40개
    '프로그래밍', '소프트웨어', '하드웨어', '알고리즘', '데이터베이스', '인공지능', '머신러닝', '딥러닝', '빅데이터', '블록체인',
    '스마트워치', '가상현실', '증강현실', '메타버스', '자율주행', '전기자동차', '태양광발전', '풍력발전', '친환경에너지', '탄소중립',
    '디지털전환', '원격근무', '화상회의', '온라인쇼핑', '모바일결제', '비대면서비스', '언택트문화', '뉴노멀시대', '코로나바이러스', '백신접종',
    '반도체산업', '디스플레이', '스마트팩토리', '로봇공학', '드론기술', '우주항공', '바이오기술', '나노기술', '양자컴퓨터', '사이버보안',
]

# 추가 한글 속담 (총 60+ 개)
EXTRA_KO_PROVERBS = [
    # 초급 (8-18자)
    '구슬이 서 말이라도 꿰어야 보배',
    '고래 싸움에 새우 등 터진다',
    '까마귀 날자 배 떨어진다',
    '남의 잔치에 감 놓아라 배 놓아라',
    '늦게 배운 도둑이 날 새는 줄 모른다',
    '말 한마디에 천 냥 빚도 갚는다',
    '목마른 사람이 우물 판다',
    '미꾸라지 한 마리가 온 웅덩이 흐린다',
    '밑 빠진 독에 물 붓기',
    '바늘 가는 데 실 간다',
    '아닌 밤중에 홍두깨',
    '윗물이 맑아야 아랫물이 맑다',
    '입에 쓴 약이 몸에 좋다',
    '작은 고추가 더 맵다',
    '호미로 막을 것을 가래로 막는다',
    
    # 중급 (19-30자)
    '개구리 올챙이 적 생각 못한다',
    '꿩 대신 닭',
    '누워서 침 뱉기',
    '도토리 키 재기',
    '똥 묻은 개가 겨 묻은 개 나무란다',
    '마른하늘에 날벼락',
    '배보다 배꼽이 더 크다',
    '소귀에 경 읽기',
    '티끌 모아 태산',
    '한 술 밥에 배 부르랴',
    '가는 날이 장날',
    '고양이 목에 방울 달기',
    '그림의 떡',
    '남의 떡이 커 보인다',
    '찬물도 위아래가 있다',
    
    # 고급 (31-60자)
    '지렁이도 밟으면 꿈틀한다',
    '칼로 물 베기',
    '핑계 없는 무덤 없다',
    '하늘의 별 따기',
    '호랑이 굴에 들어가야 호랑이 새끼를 잡는다',
    '뛰는 놈 위에 나는 놈 있다',
    '살림살이는 늘려 가고 자식 공부는 줄여 간다',
    '선무당이 사람 잡는다',
    '세월 앞에 장사 없다',
    '소문난 잔치에 먹을 것 없다',
]


class Command(BaseCommand):
    help = '추가 한글 단어/속담을 import합니다.'

    def handle(self, *args, **options):
        batch_id = f'import-ko-extra-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 추가 한글 콘텐츠 import 시작... (batch_id: {batch_id})')
        
        # 단어 팩
        word_packs = {
            1: TextPack.objects.filter(code='ko-word-daily-1').first(),
            2: TextPack.objects.filter(code='ko-word-daily-2').first(),
            3: TextPack.objects.filter(code='ko-word-daily-3').first(),
        }
        
        # 속담 팩
        proverb_packs = {
            1: TextPack.objects.filter(code='ko-short-proverb-1').first(),
            2: TextPack.objects.filter(code='ko-short-proverb-2').first(),
            3: TextPack.objects.filter(code='ko-short-proverb-3').first(),
        }
        
        # 단어 import
        word_stats = {1: 0, 2: 0, 3: 0}
        for word in EXTRA_KO_WORDS:
            word = word.strip()
            length = len(word)
            
            if length <= 3:
                difficulty = 1
            elif length <= 5:
                difficulty = 2
            else:
                difficulty = 3
            
            pack = word_packs.get(difficulty)
            if not pack:
                continue
            
            normalized = TextItem.normalize_text(word, 'ko')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=word,
                normalized_content=normalized,
                source_name='extra_data',
                import_batch_id=batch_id,
            )
            word_stats[difficulty] += 1
        
        # 속담 import
        proverb_stats = {1: 0, 2: 0, 3: 0}
        for proverb in EXTRA_KO_PROVERBS:
            proverb = proverb.strip()
            length = len(proverb)
            
            if length <= 18:
                difficulty = 1
            elif length <= 30:
                difficulty = 2
            else:
                difficulty = 3
            
            pack = proverb_packs.get(difficulty)
            if not pack:
                continue
            
            normalized = TextItem.normalize_text(proverb, 'ko')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized).exists():
                continue
            
            TextItem.objects.create(
                pack=pack,
                content=proverb,
                normalized_content=normalized,
                source_name='extra_data',
                import_batch_id=batch_id,
            )
            proverb_stats[difficulty] += 1
        
        self.stdout.write('\n📊 결과 통계:')
        self.stdout.write('  [단어]')
        self.stdout.write(f'    - 초급: {word_stats[1]}개')
        self.stdout.write(f'    - 중급: {word_stats[2]}개')
        self.stdout.write(f'    - 고급: {word_stats[3]}개')
        self.stdout.write('  [속담]')
        self.stdout.write(f'    - 초급: {proverb_stats[1]}개')
        self.stdout.write(f'    - 중급: {proverb_stats[2]}개')
        self.stdout.write(f'    - 고급: {proverb_stats[3]}개')
        self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
