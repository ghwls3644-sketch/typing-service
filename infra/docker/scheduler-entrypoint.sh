#!/bin/sh
# 스케줄러 엔트리포인트
# 매일/매주 Django management command를 실행합니다.
# python:3.11-slim에는 cron이 없으므로 순수 shell 루프로 구현합니다.

echo "[scheduler] 스케줄러 시작 (KST 기준)"

# 시작 시 즉시 한 번 실행 (서버 재시작/첫 기동 시)
echo "[scheduler] 초기 실행: generate_daily_challenge"
python manage.py generate_daily_challenge 2>&1 || echo "[scheduler] 데일리 챌린지 생성 실패 (데이터 없을 수 있음)"

while true; do
    # 현재 KST 시간 가져오기
    HOUR=$(TZ=Asia/Seoul date +%H)
    MINUTE=$(TZ=Asia/Seoul date +%M)
    DOW=$(TZ=Asia/Seoul date +%u)  # 1=월, 7=일

    # 매일 00:00 KST → 데일리 챌린지 생성
    if [ "$HOUR" = "00" ] && [ "$MINUTE" = "00" ]; then
        echo "[scheduler] $(TZ=Asia/Seoul date) - 데일리 챌린지 생성"
        python manage.py generate_daily_challenge >> /app/logs/scheduler.log 2>&1
    fi

    # 매주 월요일 00:10 KST → 주간 리더보드 스냅샷
    if [ "$DOW" = "1" ] && [ "$HOUR" = "00" ] && [ "$MINUTE" = "10" ]; then
        echo "[scheduler] $(TZ=Asia/Seoul date) - 주간 리더보드 스냅샷"
        python manage.py generate_weekly_snapshot >> /app/logs/scheduler.log 2>&1
    fi

    # 60초마다 체크
    sleep 60
done
