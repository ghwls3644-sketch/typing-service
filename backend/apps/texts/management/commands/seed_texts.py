"""
타자 연습용 샘플 텍스트 데이터 시딩 커맨드
Usage: python manage.py seed_texts
"""
from django.core.management.base import BaseCommand
from apps.texts.models import TextPack, TextItem


class Command(BaseCommand):
    help = '타자 연습용 샘플 텍스트 데이터를 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write('📦 샘플 텍스트 데이터 생성 시작...')
        
        # 한글 문장 팩
        korean_sentences = [
            '하늘 아래 첫 동네에 봄이 찾아왔다.',
            '빠른 갈색 여우가 게으른 개를 뛰어넘는다.',
            '오늘도 좋은 하루가 되기를 바랍니다.',
            '타자 연습은 꾸준히 하면 실력이 늘어납니다.',
            '컴퓨터 자판을 익히면 업무 효율이 올라갑니다.',
            '매일 조금씩 연습하면 어느새 달인이 됩니다.',
            '키보드를 보지 않고 치는 것이 목표입니다.',
            '정확하게 치는 것이 빠르게 치는 것보다 중요합니다.',
            '손가락을 홈 키에 올려놓고 시작하세요.',
            '블라인드 타이핑은 모든 직장인의 필수 스킬입니다.',
            '꾸준한 연습만이 실력 향상의 지름길입니다.',
            '오타를 줄이면 자연스럽게 속도가 빨라집니다.',
            '하루에 10분씩만 연습해도 효과가 있습니다.',
            '타자 연습 프로그램으로 재미있게 연습하세요.',
            '목표를 세우고 조금씩 달성해 나가세요.',
        ]
        
        korean_pack, created = TextPack.objects.get_or_create(
            title='기본 한글 문장',
            language='ko',
            defaults={
                'difficulty': 2,
                'source': 'admin',
                'description': '타자 연습을 위한 기본 한글 문장 모음입니다.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✅ Pack 생성: {korean_pack.title}')
            for i, content in enumerate(korean_sentences):
                TextItem.objects.create(
                    pack=korean_pack,
                    content=content,
                    length=len(content.replace(' ', '')),
                    order=i
                )
            self.stdout.write(f'     → {len(korean_sentences)}개 문장 추가')
        else:
            self.stdout.write(f'  ⏭️ Pack 이미 존재: {korean_pack.title}')
        
        # 영어 문장 팩
        english_sentences = [
            'The quick brown fox jumps over the lazy dog.',
            'Practice makes perfect in everything we do.',
            'Typing skills improve with consistent practice.',
            'Hello world, this is a typing practice app.',
            'Learning to type fast requires patience and dedication.',
            'Keep your fingers on the home row keys.',
            'Speed will come naturally with accuracy first.',
            'Every expert was once a beginner at typing.',
            'Focus on accuracy before increasing your speed.',
            'Touch typing is an essential skill in the digital age.',
            'Regular practice leads to significant improvement.',
            'Position your hands correctly on the keyboard.',
            'Consistent effort yields remarkable results.',
            'Typing without looking at the keyboard saves time.',
            'Small daily improvements lead to stunning results.',
        ]
        
        english_pack, created = TextPack.objects.get_or_create(
            title='Basic English Sentences',
            language='en',
            defaults={
                'difficulty': 2,
                'source': 'admin',
                'description': 'Basic English sentences for typing practice.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✅ Pack 생성: {english_pack.title}')
            for i, content in enumerate(english_sentences):
                TextItem.objects.create(
                    pack=english_pack,
                    content=content,
                    length=len(content.replace(' ', '')),
                    order=i
                )
            self.stdout.write(f'     → {len(english_sentences)}개 문장 추가')
        else:
            self.stdout.write(f'  ⏭️ Pack 이미 존재: {english_pack.title}')
        
        # 한글 고급 문장 팩
        korean_advanced = [
            '인공지능 기술의 발전은 우리 삶의 많은 부분을 변화시키고 있습니다.',
            '프로그래밍 언어를 배우는 것은 논리적 사고력을 향상시킵니다.',
            '클라우드 컴퓨팅은 현대 IT 인프라의 핵심 기술입니다.',
            '사이버 보안의 중요성은 날로 증가하고 있습니다.',
            '빅데이터 분석을 통해 의미 있는 인사이트를 도출할 수 있습니다.',
            '소프트웨어 개발은 체계적인 프로세스를 따라야 합니다.',
            '사용자 경험 디자인은 제품 성공의 핵심 요소입니다.',
            '데이터베이스 설계는 시스템 성능에 큰 영향을 미칩니다.',
        ]
        
        korean_adv_pack, created = TextPack.objects.get_or_create(
            title='IT 전문 용어 문장',
            language='ko',
            defaults={
                'difficulty': 4,
                'source': 'admin',
                'description': 'IT 관련 전문 용어가 포함된 고급 문장입니다.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✅ Pack 생성: {korean_adv_pack.title}')
            for i, content in enumerate(korean_advanced):
                TextItem.objects.create(
                    pack=korean_adv_pack,
                    content=content,
                    length=len(content.replace(' ', '')),
                    order=i
                )
            self.stdout.write(f'     → {len(korean_advanced)}개 문장 추가')
        else:
            self.stdout.write(f'  ⏭️ Pack 이미 존재: {korean_adv_pack.title}')
        
        self.stdout.write(self.style.SUCCESS('✅ 샘플 텍스트 데이터 생성 완료!'))
