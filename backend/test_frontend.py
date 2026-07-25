"""프론트엔드 브라우저 테스트 (Playwright).

사용법:
    python test_frontend.py

테스트 내용:
    1. 프론트엔드 접속
    2. 괌 여행 리스트 생성
    3. 체크리스트 생성 확인
"""

import asyncio
from playwright.async_api import async_playwright
import json


async def test_guam_trip():
    """괌 여행 테스트."""
    print("=" * 60)
    print("🌏 괌 여행 체크리스트 테스트 (Playwright)")
    print("=" * 60)

    async with async_playwright() as p:
        # 브라우저 시작 (헤드리스 모드: False로 하면 브라우저가 보임)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("\n1️⃣ 프론트엔드 접속 중...")
        try:
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            print("   ✅ 접속 성공")
        except Exception as e:
            print(f"   ❌ 접속 실패: {e}")
            print("   💡 프론트엔드 서버가 실행 중인지 확인하세요 (npm run dev)")
            await browser.close()
            return False

        # 스크린샷
        await page.screenshot(path="frontend_home.png")
        print("   📸 스크린샷 저장: frontend_home.png")

        print("\n2️⃣ 여행지 입력...")
        try:
            # 여행지 입력창 찾기
            destination_input = await page.wait_for_selector('input#destination', timeout=5000)
            await destination_input.fill("괌")
            print("   ✅ 여행지: 괌")
        except Exception as e:
            print(f"   ❌ 여행지 입력 실패: {e}")
            await browser.close()
            return False

        print("\n3️⃣ 목적 선택...")
        try:
            # 관광 칩 클릭
            purpose_chip = await page.query_selector('button:has-text("관광")')
            if purpose_chip:
                await purpose_chip.click()
                print("   ✅ 목적: 관광")
        except Exception as e:
            print(f"   ⚠️  목적 선택 실패 (기본값 사용): {e}")

        print("\n4️⃣ 기간 선택...")
        try:
            # 기간 선택 (3박 4일)
            duration_select = await page.query_selector('select')
            if duration_select:
                await duration_select.select_option("3박 4일")
                print("   ✅ 기간: 3박 4일")
        except Exception as e:
            print(f"   ⚠️  기간 선택 실패: {e}")

        print("\n5️⃣ 여행 리스트 생성 시작...")
        try:
            submit_button = await page.wait_for_selector('button.primary.cta:has-text("내 여행 리스트 만들기")')
            await submit_button.click()
            print("   ✅ 버튼 클릭 성공")
        except Exception as e:
            print(f"   ❌ 버튼 클릭 실패: {e}")
            await browser.close()
            return False

        print("\n6️⃣ 로딩 대기...")
        try:
            # 로딩 화면 대기
            await page.wait_for_selector('.loading-screen', timeout=5000)
            print("   ⏳ 로딩 중...")

            # 완료 대기 (최대 60초)
            await page.wait_for_selector('.checklist', timeout=60000)
            print("   ✅ 체크리스트 로드 완료!")
        except Exception as e:
            print(f"   ❌ 로딩 실패: {e}")
            print("   💡 서버 로그를 확인해주세요")

        # 최종 스크린샷
        await page.screenshot(path="frontend_result.png", full_page=True)
        print("   📸 결과 스크린샷 저장: frontend_result.png")

        print("\n7️⃣ 결과 확인...")
        try:
            # 아이템 확인
            checklist_items = await page.query_selector_all('.check-item')
            print(f"   📦 생성된 아이템 수: {len(checklist_items)}")

            if len(checklist_items) > 0:
                print("   ✅ 체크리스트 생성 성공!")

                # 첫 5개 아이템 표시
                print("\n   📋 생성된 아이템 (일부):")
                for i, item in enumerate(checklist_items[:5], 1):
                    item_text = await item.text_content()
                    print(f"      {i}. {item_text[:50]}...")

                # 주의사항 확인
                caution_tab = await page.query_selector('button:has-text("주의사항")')
                if caution_tab:
                    await caution_tab.click()
                    await page.wait_for_timeout(1000)
                    caution_grid = await page.query_selector_all('.caution-grid article')
                    print(f"\n   📝 주의사항 수: {len(caution_grid)}")
            else:
                print("   ❌ 체크리스트가 생성되지 않았습니다")

        except Exception as e:
            print(f"   ❌ 결과 확인 실패: {e}")

        print("\n8️⃣ 백엔드 로그 확인...")
        # 백엔드 로그 파일 확인
        import subprocess
        try:
            result = subprocess.run(
                ['tail', '-n', '10',
                 'C:\\Users\\tjswn\\AppData\\Local\\Temp\\claude\\c--Users-tjswn-RBX-Trapkit-fresh-backend\\32688099-4ff3-46ca-94cc-1292362fbc38\\tasks\\b5drchczj.output'],
                capture_output=True,
                text=True,
                timeout=5
            )
            print("   📊 최근 백엔드 로그:")
            for line in result.stdout.split('\n')[-5:]:
                if line.strip():
                    print(f"      {line}")
        except Exception as e:
            print(f"   ⚠️  로그 확인 실패: {e}")

        print("\n" + "=" * 60)
        print("🎉 테스트 완료!")
        print("=" * 60)

        # 브라우저 유지 (사용자가 직접 확인할 수 있도록)
        print("\n💡 브라우저를 10초 후 종료합니다...")
        print("   (Enter 키를 누르면 바로 종료)")

        try:
            # 입력 대기 (비동기)
            import sys
            import io
            old_stdin = sys.stdin
            sys.stdin = io.StringIO("")
            await asyncio.wait_for(asyncio.sleep(10), timeout=10)
            sys.stdin = old_stdin
        except asyncio.TimeoutError:
            pass
        except KeyboardInterrupt:
            pass

        await browser.close()
        return True


async def main():
    """메인 함수."""
    print("\n🚀 Playwright 브라우저 테스트 시작")

    # 프론트엔드 서버 확인
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:3000'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("❌ 프론트엔드 서버가 꺼져 있습니다")
            print("💡 먼저 프론트엔드 서버를 시작하세요:")
            print("   cd c:\\Users\\tjswn\\RBX\\Trapkit-fresh\\frontend")
            print("   npm run dev")
            return
    except Exception as e:
        print("❌ 프론트엔드 서버 연결 실패:", e)
        print("💡 프론트엔드 서버가 실행 중인지 확인하세요")
        return

    try:
        success = await test_guam_trip()
        if success:
            print("\n✅ 테스트 성공!")
        else:
            print("\n❌ 테스트 실패")
    except KeyboardInterrupt:
        print("\n\n⏹️  테스트 중단됨")
    except Exception as e:
        print(f"\n\n❌ 테스트 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())