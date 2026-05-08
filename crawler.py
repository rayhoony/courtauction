import asyncio
import json
import os
import re
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=True로 변경하면 창 없이 실행
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("사이트 접속 중...")
        await page.goto("https://www.dooinauction.com/", wait_until="networkidle")

        title = await page.title()
        print(f"페이지 제목: {title}")
        print(f"현재 URL: {page.url}")

        # 메뉴 클릭
        selector = "#header > div.header_top > div.wrap > div.fright.topMenu > span:nth-child(3)"
        await page.wait_for_selector(selector)
        await page.click(selector)
        print("로그인 메뉴 클릭 완료")

        await page.wait_for_load_state("networkidle")
        print(f"클릭 후 URL: {page.url}")

        # 로그인 정보 입력
        await page.wait_for_selector("#client_id")
        crawler_id = os.environ["CRAWLER_ID"]
        crawler_password = os.environ["CRAWLER_PASSWORD"]
        await page.fill("#client_id", crawler_id)
        await page.fill("#passwd", crawler_password)
        await page.click("#loginBtn")
        print("로그인 버튼 클릭 완료")

        await page.wait_for_load_state("networkidle")
        print(f"로그인 후 URL: {page.url}")

        # GNB 첫 번째 메뉴 클릭
        gnb_selector = "#gnb > li:nth-child(1) > a"
        await page.wait_for_selector(gnb_selector)
        await page.click(gnb_selector)
        print("GNB 첫 번째 메뉴 클릭 완료")

        await page.wait_for_load_state("networkidle")
        print(f"클릭 후 URL: {page.url}")

        # #siCd 에서 '서울' 선택
        await page.wait_for_selector("#siCd")
        tag = await page.eval_on_selector("#siCd", "el => el.tagName.toLowerCase()")
        if tag == "select":
            await page.select_option("#siCd", label="서울")
        else:
            await page.click("#siCd")
            await page.click(f"text=서울")
        print("시도 '서울' 선택 완료")

        # #adrPl_btn 버튼 클릭
        await page.wait_for_selector("#adrPl_btn")
        await page.click("#adrPl_btn")
        print("#adrPl_btn 버튼 클릭 완료")

        await page.wait_for_load_state("networkidle")

        # '경기' 선택 후 버튼 클릭
        await page.wait_for_selector("#siCd")
        if tag == "select":
            await page.select_option("#siCd", label="경기")
        else:
            await page.click("#siCd")
            await page.click("text=경기")
        print("시도 '경기' 선택 완료")
        await page.click("#adrPl_btn")
        print("#adrPl_btn 버튼 클릭 완료 (경기)")

        await page.wait_for_load_state("networkidle")

        # '인천' 선택 후 버튼 클릭
        await page.wait_for_selector("#siCd")
        if tag == "select":
            await page.select_option("#siCd", label="인천")
        else:
            await page.click("#siCd")
            await page.click("text=인천")
        print("시도 '인천' 선택 완료")
        await page.click("#adrPl_btn")
        print("#adrPl_btn 버튼 클릭 완료 (인천)")

        await page.wait_for_load_state("networkidle")

        # '물건 용도 펼치기' 버튼 클릭
        await page.wait_for_selector("#btn_power")
        await page.click("#btn_power")
        print("'물건 용도 펼치기' (#btn_power) 버튼 클릭 완료")

        await page.wait_for_load_state("networkidle")

        # '오피스텔(상업)' 항목 클릭
        await page.wait_for_selector("span.chk_ment:text('오피스텔(상업)')")
        await page.click("span.chk_ment:text('오피스텔(상업)')")
        print("'오피스텔(상업)' 클릭 완료")

        # '오피스텔(주거)' 항목 클릭
        await page.wait_for_selector("span.chk_ment:text('오피스텔(주거)')")
        await page.click("span.chk_ment:text('오피스텔(주거)')")
        print("'오피스텔(주거)' 클릭 완료")

        await page.wait_for_load_state("networkidle")

        # #minbAmtEnd 에서 '1억 5천만' 선택 (최저가격 최대값)
        await page.wait_for_selector("#minbAmtEnd")
        minb_tag = await page.eval_on_selector("#minbAmtEnd", "el => el.tagName.toLowerCase()")
        if minb_tag == "select":
            await page.select_option("#minbAmtEnd", label="1억 5천만")
        else:
            await page.click("#minbAmtEnd")
            await page.click("text=1억 5천만")
        print("최저가격 최대값 '1억 5천만' 선택 완료")

        # #fbCntBgn 에서 '2' 선택 (최소 유찰 횟수)
        await page.wait_for_selector("#fbCntBgn")
        fb_tag = await page.eval_on_selector("#fbCntBgn", "el => el.tagName.toLowerCase()")
        if fb_tag == "select":
            await page.select_option("#fbCntBgn", value="2")
        else:
            await page.click("#fbCntBgn")
            await page.click("text=2")
        print("최소 유찰 횟수 '2' 선택 완료")

        # 페이지 로딩 대기 (3초)
        await asyncio.sleep(3)

        # class가 pageBtn이고 텍스트가 '마지막'인 div의 id에서 숫자 추출
        maxPageNum = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('div.pageBtn');
                for (const btn of btns) {
                    if (btn.textContent.trim() === '마지막') {
                        return parseInt(btn.id.replace('loadPage_', ''));
                    }
                }
                return null;
            }
        """)
        if maxPageNum:
            print(f"최대 페이지 수: {maxPageNum}")
        else:
            print("'마지막' 페이지 버튼을 찾을 수 없음")

        # 결과 데이터 리스트 (크롤링 시작 전 auction.json 초기화)
        results = []
        with open("auction.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        print("auction.json 초기화 완료 (덮어쓰기)")

        # loadPage_1 ~ loadPage_maxPageNum 페이지 순회
        for pg in range(1, maxPageNum + 1):
            print(f"\n===== 페이지 {pg}/{maxPageNum} =====")

            # 첫 페이지가 아니면 해당 페이지 버튼 클릭
            if pg > 1:
                page_btn_selector = f"#loadPage_{pg}"
                await page.wait_for_selector(page_btn_selector)
                await page.click(page_btn_selector)
                await page.wait_for_load_state("networkidle")
                print(f"loadPage_{pg} 클릭 완료")

            # Tr_1 ~ Tr_20 순서대로 클릭 (없으면 중단)
            for i in range(1, 21):
                tr_selector = f"#Tr_{i}"

                # 매 반복마다 selector 재조회 (DOM 갱신 대비)
                tr = await page.query_selector(tr_selector)
                if tr is None:
                    print(f"#Tr_{i} 없음, 중단")
                    break

                # 새 창 열림 대기
                async with context.expect_page() as new_page_info:
                    await page.click(tr_selector)
                new_page = await new_page_info.value
                await new_page.wait_for_load_state("networkidle")
                print(f"#Tr_{i} 클릭 완료")

                # URL 추출
                url = new_page.url
                print(f"  [페이지{pg} Tr_{i}] URL: {url}")

                # 사건번호 추출
                사건번호 = ""
                cnt_selector = "#lyCnt_num > div > div.fleft > div:nth-child(1) > span.f20.bold_900"
                cnt_el = await new_page.query_selector(cnt_selector)
                if cnt_el:
                    사건번호 = (await cnt_el.inner_text()).strip()
                    print(f"  [페이지{pg} Tr_{i}] 물건번호: {사건번호}")
                else:
                    print(f"  [페이지{pg} Tr_{i}] 물건번호 셀렉터 없음")

                # 주소 추출
                주소 = await new_page.evaluate("""
                    () => {
                        const mobileTitle = document.querySelector('span.mobileTitle');
                        if (mobileTitle && mobileTitle.textContent.trim() === '소재지') {
                            const boldSpan = mobileTitle.nextElementSibling;
                            if (boldSpan && boldSpan.classList.contains('bold')) {
                                return boldSpan.textContent.trim();
                            }
                        }
                        return '';
                    }
                """)
                print(f"  [페이지{pg} Tr_{i}] 주소: {주소}")

                # 면적 추출
                면적 = ""
                base_td_selector = "#lyCnt_base > table > tbody > tr:nth-child(4) > td:nth-child(2)"
                base_td_el = await new_page.query_selector(base_td_selector)
                if base_td_el:
                    td_text = await base_td_el.inner_text()
                    면적 = td_text.replace("건물면적", "", 1).strip()
                    print(f"  [페이지{pg} Tr_{i}] 건물면적: {면적}")
                else:
                    print(f"  [페이지{pg} Tr_{i}] 4행2열 셀렉터 없음")

                # 사용승인일 추출
                사용승인일 = ""
                body_text = await new_page.inner_text("body")
                for line in body_text.splitlines():
                    if "사용승인일:" in line:
                        사용승인일 = line.split("사용승인일:")[1].strip()
                        print(f"  [페이지{pg} Tr_{i}] 사용승인일: {사용승인일}")
                        break
                if not 사용승인일:
                    print(f"  [페이지{pg} Tr_{i}] 사용승인일 정보 없음")

                # 최저가 및 최저가율 추출
                price_data = await new_page.evaluate("""
                    () => {
                        const tds = document.querySelectorAll('td.blue.right');
                        for (const td of tds) {
                            const spans = Array.from(td.querySelectorAll('span'));
                            const hasLabel = spans.some(s => s.textContent.includes('최저가'));
                            if (!hasLabel) continue;
                            const bold = spans.find(s => s.classList.contains('bold'));
                            if (bold) {
                                const text = bold.textContent;
                                const m = text.match(/[\d,]+/g);
                                const price = m ? m[m.length - 1] : '';
                                const rateMatch = text.match(/\(([^)]+)\)/);
                                const rate = rateMatch ? rateMatch[1].trim() : '';
                                return { price, rate };
                            }
                        }
                        return { price: '', rate: '' };
                    }
                """)
                최저가 = price_data.get("price", "")
                최저가율 = price_data.get("rate", "")
                # 최저가는 쉼표 포함 그대로 저장 (가독성)
                print(f"  [페이지{pg} Tr_{i}] 최저가: {최저가}")
                print(f"  [페이지{pg} Tr_{i}] 최저가율: {최저가율}")

                # 평당가격 계산 (면적에서 ㎡ 앞 숫자만 추출, 3.3 곱해서 평당 환산)
                평당가격 = ""
                area_match = re.search(r'[\d.]+(?=㎡)', 면적)
                if area_match and 최저가:
                    try:
                        area_num = float(area_match.group())
                        if area_num > 0:
                            최저가_숫자 = int(최저가.replace(",", ""))
                            평당가격 = f"{round(최저가_숫자 / area_num * 3.3):,}"
                    except (ValueError, ZeroDivisionError):
                        평당가격 = ""
                print(f"  [페이지{pg} Tr_{i}] 평당가격: {평당가격}")

                # 사용승인일이 2020년 이후인 경우에만 리스트에 추가
                try:
                    year = int(사용승인일[:4]) if 사용승인일 else 0
                except (ValueError, IndexError):
                    year = 0

                if year >= 2020:
                    results.append({
                        "사건번호": 사건번호,
                        "url": url,
                        "주소": 주소,
                        "면적": 면적,
                        "사용승인일": 사용승인일,
                        "최저가": 최저가,
                        "최저가율": 최저가율,
                        "평당가격": 평당가격,
                    })
                    print(f"  [페이지{pg} Tr_{i}] → 저장 완료")
                else:
                    print(f"  [페이지{pg} Tr_{i}] → 사용승인일 {사용승인일 or '없음'} (2020년 미만, 제외)")

                await new_page.close()

        # 결과를 JSON 파일로 저장
        with open("auction.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"데이터 저장 완료: auction.json ({len(results)}건)")

        # 페이지 스크린샷 저장
        await page.screenshot(path="screenshot.png", full_page=True)
        print("스크린샷 저장 완료: screenshot.png")

        await asyncio.sleep(5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
