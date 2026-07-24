# API 테스트 실패 해결 스크립트

# 1. Baggage Cache 함수 추가 (완료)
# ✅ shared/utils/normalizer.py에 generate_baggage_cache_key 함수 추가됨

# 2. DB 마이그레이션 생성 및 실행
Write-Host "=== DB 마이그레이션 시작 ===" -ForegroundColor Green

# 기존 마이그레이션 상태 확인
alembic current

# 새 마이그레이션 생성 (trips, items, memos 테이블)
alembic revision --autogenerate -m "Add trips, items, memos tables"

# 마이그레이션 실행
alembic upgrade head

Write-Host "=== DB 마이그레이션 완료 ===" -ForegroundColor Green

# 3. 테스트 스크립트
Write-Host "`n=== API 테스트 재시작 ===" -ForegroundColor Yellow

# Health 테스트
Write-Host "`n1. Health Check:"
curl -s http://localhost:8001/health/ | ConvertFrom-Json

# Auth 테스트
Write-Host "`n2. Signup:"
$signup = curl -s -X POST http://localhost:8001/api/auth/signup `
  -H "Content-Type: application/json" `
  -d '{"email":"fixtest@example.com","password":"test1234","nickname":"fixuser"}' | ConvertFrom-Json
$signup

# Login
Write-Host "`n3. Login:"
$login = curl -s -X POST http://localhost:8001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"fixtest@example.com","password":"test1234"}' | ConvertFrom-Json
$TOKEN = $login.access_token
Write-Host "Token: $($TOKEN.Substring(0,20))..."

# Baggage Check 테스트
Write-Host "`n4. Baggage Check:"
curl -s -X POST http://localhost:8001/api/v1/baggage/check `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"airline":"대한항공","product":"MacBook","value":15.6,"unit":"inch"}' | ConvertFrom-Json

# Trip 생성 테스트
Write-Host "`n5. Create Trip:"
curl -s -X POST http://localhost:8001/api/v1/trips `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"title":"제주 여행","destination":"제주","purpose":["관광"],"duration_nights":3,"departure_month":7,"companions":"친구"}' | ConvertFrom-Json

# Items 조회 테스트 (유효한 UUID 필요)
Write-Host "`n6. Get Items (trip_id 필요):"
curl -s -X GET "http://localhost:8001/api/v1/items/550e8400-e29b-41d4-a716-446655440000" `
  -H "Authorization: Bearer $TOKEN" | ConvertFrom-Json

Write-Host "`n=== 테스트 완료 ===" -ForegroundColor Green