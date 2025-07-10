import streamlit as st
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import io
import random
from urllib.parse import quote

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="GPT-4o 저칼로리 안주 챗봇", page_icon="🤖")
st.title("안주요정 🍶🧚‍♀️")

# API 키 확인
if not openai_api_key:
    st.error("OpenAI API 키가 설정되지 않았습니다. `.env` 파일에 `OPENAI_API_KEY=your-api-key`를 추가하거나, Streamlit Cloud의 Secrets에 설정해 주세요.")
    st.stop()

# 단계별 상태 관리
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "calorie_limit" not in st.session_state:
    st.session_state.calorie_limit = 200
if "style" not in st.session_state:
    st.session_state.style = None
if "drink" not in st.session_state:
    st.session_state.drink = None
if "ingredient" not in st.session_state:
    st.session_state.ingredient = None
if "hate" not in st.session_state:
    st.session_state.hate = ""
if "digest" not in st.session_state:
    st.session_state.digest = ""
if "menu_candidates" not in st.session_state:
    st.session_state.menu_candidates = []
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = None
if "previous_menus" not in st.session_state:
    st.session_state.previous_menus = []

# 파일 로드 함수
def load_file_data(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return None
    except Exception:
        return None

# CSV 파싱 함수
def parse_csv_data(csv_data, filename):
    try:
        if not csv_data or not csv_data.strip():
            raise ValueError("파일 내용이 비어 있습니다.")
        df = pd.read_csv(io.StringIO(csv_data), encoding='utf-8', sep=',')
        return df
    except pd.errors.ParserError:
        return None
    except ValueError:
        return None
    except Exception:
        return None

# 주종 목록 로드 함수
def load_drink_options():
    drink_menu_data = load_file_data("drink_menu_complete.csv")
    if drink_menu_data:
        drink_menu_df = parse_csv_data(drink_menu_data, "drink_menu_complete.csv")
        if drink_menu_df is not None and "주종" in drink_menu_df.columns:
            return ["소주", "맥주", "레드 와인", "화이트 와인", "스파클링 와인", "막걸리", "기타 (직접 입력)"]
    return ["소주", "맥주", "레드 와인", "화이트 와인", "스파클링 와인", "막걸리", "기타 (직접 입력)"]

# 단계별 분기
if st.session_state.step == "greeting":
    st.markdown(
        "<span style='font-size:20px;'>"
        "안녕하세요! 즐거운 술자리를 계획하고 계시군요. 😊<br>"
        "저칼로리 안주를 추천해드릴게요!<br>"
        f"최대 허용 칼로리는 {st.session_state.calorie_limit}kcal로 설정되어 있는데 괜찮으신가요?<br>"
        "</span>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        yes_clicked = st.button("👍 예", key="yes_btn", use_container_width=True)
    with col2:
        no_clicked = st.button("👎 아니오", key="no_btn", use_container_width=True)

    if yes_clicked:
        st.session_state.step = "style"
        st.rerun()
    if no_clicked:
        st.session_state.step = "calorie_input"
        st.rerun()

elif st.session_state.step == "calorie_input":
    st.markdown(
        "<span style='font-size:20px;'>원하는 최대 칼로리를 숫자로 입력하세요 (예: 350)</span>",
        unsafe_allow_html=True
    )
    new_limit = st.text_input(
        "",
        value=str(st.session_state.calorie_limit),
        key="new_limit_text"
    )
    if st.button("칼로리 설정 완료", key="set_calorie_btn"):
        try:
            st.session_state.calorie_limit = int(new_limit)
            st.session_state.step = "style"
            st.rerun()
        except ValueError:
            st.warning("숫자만 입력해 주세요.")

elif st.session_state.step == "style":
    st.markdown(
        "<span style='font-size:20px;'>어떤 안주 스타일이 끌리시나요?</span>",
        unsafe_allow_html=True
    )
    style_options = [
        "난 무조건 고단백파! (단백질 듬뿍·지방 최소)",
        "오늘은 탄수가 땡겨요! (에너지원 듬뿍)",
        "지방 좀 넣어줄 때가 됐어! (고소한 맛)",
        "맵고짜고단거!(스트레스 격파!)",
        "에라이 모르겠다! 그냥 니가 추천해줘!"
    ]
    style_selected = st.radio(
        "",
        style_options,
        key="style_radio"
    )
    if st.button("선택 완료", key="style_submit_btn"):
        if style_selected:
            st.session_state.style = style_selected
            st.session_state.step = "drink"
            st.rerun()

elif st.session_state.step == "drink":
    st.markdown(
        "<span style='font-size:20px;'>주종을 선택하세요.</span>",
        unsafe_allow_html=True
    )
    drink_options = load_drink_options()
    drink_selected = st.radio(
        "",
        drink_options,
        key="drink_radio"
    )
    custom_drink = ""
    if drink_selected == "기타 (직접 입력)":
        custom_drink = st.text_input("주종을 직접 입력해 주세요.", placeholder="예: 위스키, 사케", key="custom_drink_input")
    if st.button("선택 완료", key="drink_submit_btn"):
        if drink_selected and (drink_selected != "기타 (직접 입력)" or custom_drink):
            st.session_state.drink = custom_drink if drink_selected == "기타 (직접 입력)" else drink_selected
            if st.session_state.get("from_no_menu_options", False):
                st.session_state.step = "recommend"
            else:
                st.session_state.step = "ingredient"
            st.rerun()

elif st.session_state.step == "ingredient":
    st.markdown(
        "<span style='font-size:20px;'>선호하는 재료를 선택하세요.</span>",
        unsafe_allow_html=True
    )
    ingredient = st.radio(
        "",
        ("고기", "해산물", "채소", "과일", "아무거나"),
        key="ingredient_radio"
    )
    if st.button("선택 완료", key="ingredient_submit_btn"):
        if ingredient:
            st.session_state.ingredient = ingredient
            if st.session_state.get("from_no_menu_options", False):
                st.session_state.step = "recommend"
            else:
                st.session_state.step = "hate"
            st.rerun()

elif st.session_state.step == "hate":
    st.markdown(
        "<span style='font-size:20px;'>싫어하는 재료나 안주가 있나요?</span>",
        unsafe_allow_html=True
    )
    hate = st.text_input("", placeholder="없으면 비워두세요", key="hate_input")
    if st.button("다음"):
        st.session_state.hate = hate
        st.session_state.step = "digest"
        st.rerun()

elif st.session_state.step == "digest":
    st.markdown(
        "<span style='font-size:20px;'>알레르기, 불내증, 소화 불편감 등 건강상 제한이 있나요?</span>",
        unsafe_allow_html=True
    )
    digest = st.text_input("", placeholder="없으면 비워두세요", key="digest_input")
    if st.button("다음"):
        st.session_state.digest = digest
        st.session_state.step = "recommend"
        st.rerun()

elif st.session_state.step == "calorie_input_again":
    st.markdown(
        "<span style='font-size:20px;'>새로운 최대 칼로리를 숫자로 입력하세요 (예: 350)</span>",
        unsafe_allow_html=True
    )
    new_limit = st.text_input(
        "",
        value=str(st.session_state.calorie_limit + 100),
        key="new_limit_text_again"
    )
    if st.button("칼로리 설정 완료", key="set_calorie_btn_again"):
        try:
            st.session_state.calorie_limit = int(new_limit)
            st.session_state.step = "recommend"
            st.rerun()
        except ValueError:
            st.warning("숫자만 입력해 주세요.")

elif st.session_state.step == "recommend":
    with st.spinner("안주를 찾는 중입니다..."):
        # 파일 로드
        food_menu_data = load_file_data("food_menu_complete.csv")
        drink_menu_data = load_file_data("drink_menu_complete.csv")
        
        # 파일 데이터 파싱
        food_menu_df = parse_csv_data(food_menu_data, "food_menu_complete.csv") if food_menu_data else None
        drink_menu_df = parse_csv_data(drink_menu_data, "drink_menu_complete.csv") if drink_menu_data else None
        
        # 메뉴 필터링
        filtered_menus = []
        drink_recommendations = []
        
        if food_menu_df is not None:
            if st.session_state.ingredient != "아무거나":
                filtered_menus = food_menu_df[food_menu_df["대분류"] == st.session_state.ingredient]["음식명"].tolist()
            else:
                filtered_menus = food_menu_df["음식명"].tolist()
            if st.session_state.hate:
                hate_list = [h.strip() for h in st.session_state.hate.split(",")]
                filtered_menus = [menu for menu in filtered_menus if all(h not in menu for h in hate_list)]
        
        # 주종별 안주 선택 (클래식 3개, 트렌드 1개, 실용적 1개)
        if drink_menu_df is not None:
            drink_pairings = drink_menu_df[drink_menu_df["주종"] == st.session_state.drink]
            classic_pairings = drink_pairings[drink_pairings["페어링 구분"] == "클래식 조합"]["추천 안주"].tolist()
            trend_pairings = drink_pairings[drink_pairings["페어링 구분"] == "트렌드 조합"]["추천 안주"].tolist()
            practical_pairings = drink_pairings[drink_pairings["페어링 구분"] == "실용적 조합"]["추천 안주"].tolist()
            
            # 이전에 추천된 메뉴 제외
            classic_pairings = [menu for menu in classic_pairings if menu not in st.session_state.previous_menus]
            trend_pairings = [menu for menu in trend_pairings if menu not in st.session_state.previous_menus]
            practical_pairings = [menu for menu in practical_pairings if menu not in st.session_state.previous_menus]
            
            # 무작위 선택 (클래식 3개 보장 시 데이터 부족 시 GPT에 보완 요청)
            selected_classics = random.sample(classic_pairings, min(3, len(classic_pairings))) if classic_pairings else []
            selected_trend = random.sample(trend_pairings, min(1, len(trend_pairings))) if trend_pairings else []
            selected_practical = random.sample(practical_pairings, min(1, len(practical_pairings))) if practical_pairings else []
            
            # 데이터 부족 시 GPT에 보완 요청
            if len(selected_classics) < 3:
                additional_classics_needed = 3 - len(selected_classics)
                prompt_addition = f"클래식 스타일 안주 {additional_classics_needed}개를 추가로 추천해 주세요."
            else:
                prompt_addition = ""
            
            # 선택된 안주 결합
            drink_recommendations = selected_classics + selected_trend + selected_practical
        
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = (
            f"당신은 저칼로리 안주 추천 챗봇입니다.\n"
            f"조건:\n"
            f"- 최대 칼로리: {st.session_state.calorie_limit}kcal (100g 기준으로 초과하지 않는 메뉴만 추천)\n"
            f"- 안주 스타일: {st.session_state.style}\n"
            f"- 주종: {st.session_state.drink}\n"
            f"- 선호 재료: {st.session_state.ingredient}\n"
            f"- 싫어하는 재료/안주: {st.session_state.hate}\n"
            f"- 건강 제한: {st.session_state.digest}\n"
            f"다음 메뉴 목록에서 조건에 맞는 배달 가능한 저칼로리 안주 메뉴 5가지를 추천해 주세요:\n"
            f"{', '.join(filtered_menus) if filtered_menus else '모든 메뉴'}\n"
            f"주종({st.session_state.drink})에 어울리는 추천 안주:\n"
            f"{', '.join(drink_recommendations) if drink_recommendations else '없음'}\n"
            f"이전에 추천된 메뉴({', '.join(st.session_state.previous_menus) if st.session_state.previous_menus else '없음'})는 제외하고 새로운 메뉴를 추천해 주세요.\n"
            f"각 메뉴는 이름, 예상 칼로리(100g 기준), 추천 이유를 포함해 주세요. 추천 메뉴는 총 5개로, 클래식 스타일 3개, 트렌드 스타일 1개, 실용적 스타일 1개를 반영해 주세요. {prompt_addition}\n"
            f"추가로, 각 메뉴 아래에 사용자가 '이게 왜 어울리지?'라고 질문할 수 있으니, 트렌드와 실용적 스타일에 대해 한 줄씩 설명을 추가해 주세요. 설명은 실제 사례, 뉴스, 기사 기반으로 구체적으로 작성해 주세요. 예: '2025년 7월 KBS 뉴스에서 소개된 조합입니다' 또는 '최근 한국 요리 트렌드 보고서에 따르면...'처럼 출처를 명시해 주세요.\n"
            f"답변은 번호 목록으로 해주세요 (예: 1. 메뉴 이름 - 칼로리(100g 기준) - 추천 이유 - [설명])."
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 저칼로리 안주 추천 챗봇입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message.content.strip()
        new_menus = [line.split(" - ")[0].replace(f"{i}. ", "").strip() for i in range(1, 6) for line in bot_reply.split("\n") if line.startswith(f"{i}.")]
        st.session_state.previous_menus.extend(new_menus)
        st.session_state.menu_candidates = bot_reply
        st.session_state.step = "show_menu"
        st.rerun()

elif st.session_state.step == "show_menu":
    st.markdown("<span style='font-size:20px;'>**추천 메뉴 (100g 기준):**</span>", unsafe_allow_html=True)
    st.markdown(st.session_state.menu_candidates)
    st.markdown("<span style='font-size:20px;'>마음에 드는 번호를 눌러주세요.</span>", unsafe_allow_html=True)
    menu_options = ["1", "2", "3", "4", "5", "마음에 드는 메뉴가 없어요"]
    menu_selection = st.radio("", menu_options, key="menu_selection_radio")
    if st.button("선택 완료"):
        if menu_selection in ["1", "2", "3", "4", "5"]:
            st.session_state.selected_menu = menu_selection
            st.session_state.step = "location"
            st.rerun()
        elif menu_selection == "마음에 드는 메뉴가 없어요":
            st.session_state.step = "no_menu_options"
            st.rerun()

elif st.session_state.step == "no_menu_options":
    st.markdown("<span style='font-size:20px;'>어떤 옵션을 선택하시겠습니까?</span>", unsafe_allow_html=True)
    no_menu_choice = st.radio(
        "",
        ["다른 안주 더보기", "칼로리 변경", "식재료 바꾸기", "주종 바꾸기"],
        key="no_menu_choice_radio"
    )
    if st.button("선택 완료"):
        if no_menu_choice == "다른 안주 더보기":
            st.session_state.step = "recommend"
        elif no_menu_choice == "칼로리 변경":
            st.session_state.step = "calorie_input_again"
        elif no_menu_choice == "식재료 바꾸기":
            st.session_state.from_no_menu_options = True
            st.session_state.ingredient = None
            st.session_state.step = "ingredient"
        elif no_menu_choice == "주종 바꾸기":
            st.session_state.from_no_menu_options = True
            st.session_state.drink = None
            st.session_state.step = "drink"
        st.rerun()

elif st.session_state.step == "location":
    st.markdown(
        "<span style='font-size:20px;'>선택한 메뉴를 동네에서 찾아드릴게요. 동네를 입력하고 '위치 안내' 누르면 카카오맵에서 확인하세요.</span>",
        unsafe_allow_html=True
    )
    region = st.text_input("", placeholder="예: 왕십리", key="region_input")
    if st.button("위치 안내"):
        if region and st.session_state.selected_menu:
            menu_lines = st.session_state.menu_candidates.split("\n")
            selected_menu_name = None
            for line in menu_lines:
                if line.startswith(f"{st.session_state.selected_menu}."):
                    selected_menu_name = line.split(" - ")[0].replace(f"{st.session_state.selected_menu}. ", "").strip()
                    break
            if selected_menu_name:
                map_url = f"https://map.kakao.com/?q={quote(region + ' ' + selected_menu_name)}"
                st.markdown(f'[카카오맵에서 열기]({map_url})', unsafe_allow_html=True)
            else:
                st.warning("선택한 메뉴를 찾을 수 없습니다. 다시 선택해 주세요.")
        elif not region:
            st.warning("동네를 입력해 주세요.")
        if st.button("확인 완료"):
            st.session_state.step = "diet_tip"
            st.rerun()

elif st.session_state.step == "diet_tip":
    st.markdown(
        "<span style='font-size:20px;'>소중한 분들과 즐거운 시간 보내세요. 내일은 건강을 위해 가벼운 러닝이나 간헐적 단식, 반신욕 등을 실천해 보세요😊</span>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("처음으로"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.button("닫기"):
            st.stop()