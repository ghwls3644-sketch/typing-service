"""
한글 속담 배치 import 커맨드
Usage: python manage.py import_ko_proverbs [--file FILE]
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem
import unicodedata
import re
import uuid


# 샘플 한글 속담 데이터
SAMPLE_KO_PROVERBS = [
    # 초급 (8-18자)
    '가는 말이 고와야 오는 말이 곱다',
    '낮말은 새가 듣고 밤말은 쥐가 듣는다',
    '등잔 밑이 어둡다',
    '서당 개 삼 년이면 풍월을 읊는다',
    '원숭이도 나무에서 떨어진다',
    '호랑이도 제 말 하면 온다',
    '백문이 불여일견',
    '고생 끝에 낙이 온다',
    '쥐구멍에도 볕 들 날 있다',
    '누워서 떡 먹기',
    '가재는 게 편',
    '꿩 먹고 알 먹고',
    '돌다리도 두들겨 보고 건너라',
    '소 잃고 외양간 고친다',
    
    # 중급 (19-30자)
    '하늘이 무너져도 솟아날 구멍이 있다',
    '천 리 길도 한 걸음부터',
    '세 살 버릇 여든까지 간다',
    '콩 심은 데 콩 나고 팥 심은 데 팥 난다',
    '작은 고추가 맵다',
    '발 없는 말이 천 리 간다',
    '가랑비에 옷 젖는 줄 모른다',
    '공든 탑이 무너지랴',
    '시작이 반이다',
    '아니 땐 굴뚝에 연기 나랴',
    '배보다 배꼽이 더 크다',
    '빈 수레가 요란하다',
    '우물 안 개구리',
    '티끌 모아 태산',
    
    # 고급 (31-60자)
    '뛰는 놈 위에 나는 놈 있다',
    '못 먹는 감 찔러나 본다',
    '가뭄에 콩 나듯',
    '남의 떡이 커 보인다',
    '울며 겨자 먹기',
    '낫 놓고 기역 자도 모른다',
    '되로 주고 말로 받는다',
    '바늘 도둑이 소 도둑 된다',
    '사공이 많으면 배가 산으로 간다',
    '열 번 찍어 안 넘어가는 나무 없다',
]


def is_valid_ko_proverb(text: str) -> tuple[bool, str]:
    """한글 속담 유효성 검사 (강한 필터)"""
    # 한글 + 공백만 허용
    if not all('\uAC00' <= c <= '\uD7A3' or c == ' ' for c in text):
        return False, 'invalid_chars'
    
    # 길이 제한 (8-60자)
    length = len(text)
    if length < 8 or length > 60:
        return False, 'invalid_length'
    
    return True, ''


def get_difficulty(text: str) -> int:
    """속담 길이 기반 난이도 분류"""
    length = len(text)
    if length <= 18:
        return 1  # 초급
    elif length <= 30:
        return 2  # 중급
    else:
        return 3  # 고급


def normalize_ko_proverb(text: str) -> str:
    """한글 속담 정규화"""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # 연속 공백 -> 1개
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[.!?]+$', '', text)  # 끝 문장부호 제거
    return text


class Command(BaseCommand):
    help = '한글 속담을 배치로 import합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='속담 목록 파일 경로 (없으면 샘플 데이터 사용)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 저장하지 않고 시뮬레이션만 수행'
        )

    def handle(self, *args, **options):
        batch_id = f'import-ko-proverbs-{uuid.uuid4().hex[:8]}'
        self.stdout.write(f'📦 한글 속담 배치 import 시작... (batch_id: {batch_id})')
        
        # 속담 로드
        if options['file']:
            with open(options['file'], 'r', encoding='utf-8') as f:
                proverbs = [line.strip() for line in f if line.strip()]
        else:
            proverbs = SAMPLE_KO_PROVERBS
        
        # 통계
        stats = {
            'input': len(proverbs),
            'filtered': 0,
            'duplicated': 0,
            'inserted': 0,
            'by_difficulty': {1: 0, 2: 0, 3: 0}
        }
        dropped_samples = []
        
        # 팩 가져오기
        packs = {
            1: TextPack.objects.filter(code='ko-short-proverb-1').first(),
            2: TextPack.objects.filter(code='ko-short-proverb-2').first(),
            3: TextPack.objects.filter(code='ko-short-proverb-3').first(),
        }
        
        for diff, pack in packs.items():
            if not pack:
                self.stdout.write(self.style.ERROR(f'  ❌ 팩 없음: ko-short-proverb-{diff}'))
                return
        
        # 속담 처리
        for proverb in proverbs:
            # 정규화
            normalized = normalize_ko_proverb(proverb)
            
            # 유효성 검사
            valid, reason = is_valid_ko_proverb(normalized)
            if not valid:
                stats['filtered'] += 1
                if len(dropped_samples) < 50:
                    dropped_samples.append({'text': proverb, 'reason': reason})
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
                self.stdout.write(f'  - "{sample["text"][:30]}...": {sample["reason"]}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n⚠️ Dry run - 실제 저장되지 않음'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ 완료! batch_id: {batch_id}'))
