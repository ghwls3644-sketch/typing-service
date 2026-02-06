"""
한글 단어 배치 import 커맨드
Usage: python manage.py import_ko_words [--file FILE]
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import unicodedata
import re
import uuid


# 샘플 한글 단어 데이터 (실제 운영시 외부 파일에서 로드)
SAMPLE_KO_WORDS = [
    # 초급 (2-3글자)
    '사과', '바나나', '포도', '딸기', '수박',
    '학교', '집', '책', '연필', '지우개',
    '엄마', '아빠', '형', '누나', '동생',
    '하늘', '바다', '산', '강', '들',
    '나무', '꽃', '풀', '새', '물고기',
    '빨강', '파랑', '노랑', '초록', '보라',
    '하나', '둘', '셋', '넷', '다섯',
    '맛', '향', '색', '소리', '촉감',
    
    # 중급 (4-5글자)
    '컴퓨터', '스마트폰', '태블릿', '노트북', '모니터',
    '프로그램', '소프트웨어', '하드웨어', '네트워크', '인터넷',
    '알고리즘', '데이터', '서버', '클라우드', '데이터베이스',
    '개발자', '디자이너', '프로젝트', '회의실', '사무실',
    '커피숍', '레스토랑', '백화점', '마트', '편의점',
    '비행기', '기차', '자동차', '자전거', '오토바이',
    
    # 고급 (6글자 이상)
    '인공지능', '머신러닝', '딥러닝', '빅데이터분석', '클라우드컴퓨팅',
    '사이버보안', '블록체인', '암호화폐', '가상현실', '증강현실',
    '프로그래밍', '객체지향', '함수형프로그래밍', '반응형디자인', '사용자경험',
    '지속가능성', '기후변화', '재생에너지', '친환경제품', '탄소중립',
]


def is_valid_ko_word(word: str) -> tuple[bool, str]:
    """한글 단어 유효성 검사"""
    # 공백 포함 불가
    if ' ' in word:
        return False, 'contains_space'
    
    # 한글만 허용
    if not all('\uAC00' <= c <= '\uD7A3' for c in word):
        return False, 'not_hangul'
    
    # 길이 제한 (2-10글자)
    if len(word) < 2 or len(word) > 10:
        return False, 'invalid_length'
    
    return True, ''


def get_difficulty(word: str) -> int:
    """단어 길이 기반 난이도 분류"""
    length = len(word)
    if length <= 3:
        return 1  # 초급
    elif length <= 5:
        return 2  # 중급
    else:
        return 3  # 고급


def normalize_ko_word(word: str) -> str:
    """한글 단어 정규화"""
    word = word.strip()
    word = unicodedata.normalize('NFC', word)
    return word


class Command(BaseCommand):
    help = '한글 단어를 배치로 import합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='단어 목록 파일 경로 (없으면 샘플 데이터 사용)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 저장하지 않고 시뮬레이션만 수행'
        )

    def handle(self, *args, **options):
        batch_id = f'import-ko-words-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 한글 단어 배치 import 시작... (batch_id: {batch_id})')
        
        # 단어 로드
        if options['file']:
            with open(options['file'], 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
        else:
            words = SAMPLE_KO_WORDS
        
        # 통계
        stats = {
            'input': len(words),
            'filtered': 0,
            'duplicated': 0,
            'inserted': 0,
            'by_difficulty': {1: 0, 2: 0, 3: 0}
        }
        dropped_samples = []
        
        # 팩 가져오기
        packs = {
            1: TextPack.objects.filter(code='ko-word-daily-1').first(),
            2: TextPack.objects.filter(code='ko-word-daily-2').first(),
            3: TextPack.objects.filter(code='ko-word-daily-3').first(),
        }
        
        for diff, pack in packs.items():
            if not pack:
                self.stdout.write(self.style.ERROR(f'  ❌ 팩 없음: ko-word-daily-{diff}'))
                return
        
        # 단어 처리
        for word in words:
            # 정규화
            normalized = normalize_ko_word(word)
            
            # 유효성 검사
            valid, reason = is_valid_ko_word(normalized)
            if not valid:
                stats['filtered'] += 1
                if len(dropped_samples) < 50:
                    dropped_samples.append({'word': word, 'reason': reason})
                continue
            
            # 난이도 분류
            difficulty = get_difficulty(normalized)
            pack = packs[difficulty]
            
            # 중복 검사
            normalized_for_db = TextItem.normalize_text(normalized, 'ko')
            if TextItem.objects.filter(pack=pack, normalized_content=normalized_for_db).exists():
                stats['duplicated'] += 1
                continue
            
            # 저장
            if not options['dry_run']:
                TextItem.objects.create(
                    pack=pack,
                    content=normalized,
                    normalized_content=normalized_for_db,
                    source_name='sample_data',
                    import_batch_id=batch_id,
                )
            
            stats['inserted'] += 1
            stats['by_difficulty'][difficulty] += 1
        
        # 결과 출력
        self.stdout.write('\n📊 결과 통계:')
        self.stdout.write(f'  - 입력: {stats["input"]}개')
        self.stdout.write(f'  - 필터링: {stats["filtered"]}개')
        self.stdout.write(f'  - 중복 스킵: {stats["duplicated"]}개')
        self.stdout.write(f'  - 삽입: {stats["inserted"]}개')
        self.stdout.write(f'    - 초급(1): {stats["by_difficulty"][1]}개')
        self.stdout.write(f'    - 중급(2): {stats["by_difficulty"][2]}개')
        self.stdout.write(f'    - 고급(3): {stats["by_difficulty"][3]}개')
        
        if dropped_samples:
            self.stdout.write(f'\n📋 탈락 샘플 (최대 50개):')
            for sample in dropped_samples[:10]:
                self.stdout.write(f'  - "{sample["word"]}": {sample["reason"]}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n⚠️ Dry run - 실제 저장되지 않음'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
