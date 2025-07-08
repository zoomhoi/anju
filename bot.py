import streamlit as st
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import io

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

# 파일 로드 함수 (로컬 환경)
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
    except pd.errors.ParserError as e:
        return None
    except ValueError as e:
        return None
    except Exception as e:
        return None

# 단계별 분기
if st.session_state.step == "greeting":
    st.markdown(
        "<span style='font-size:20px;'>"
        "안녕하세요! <br>"
        "즐거운 술자리를 계획하고 계시군요. 😊 <br>"
        "살 안찌면서 맛있는 안주를 추천해드릴게요.<br>"
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
        "",  # 안내문은 위에서 처리
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
        "오늘은 탄수가 땡겨요! (에너지원 든든)",
        "지방 좀 넣어줄 때가 됐어! (고소한 맛)",
        "맵고짜고단거!(스트레스 격파!)",
        "에라이 모르겠다! 그냥 니가 추천해줘!"
    ]
    style_selected = st.radio(
        "",  # 안내문은 위에서 처리
        style_options,
        key="style_radio"
    )
    if st.button("스타일 선택 완료", key="style_submit_btn"):
        if style_selected:
            st.session_state.style = style_selected
            st.session_state.step = "drink"
            st.rerun()

elif st.session_state.step == "drink":
    st.markdown(
        "<span style='font-size:20px;'>주종을 선택하세요.</span>",
        unsafe_allow_html=True
    )
    drink_options = ["소주", "맥주", "양주", "레드 와인", "화이트 와인", "스파클링 와인", "막걸리", "기타 (직접 입력)"]
    drink_selected = st.radio(
        "",  # 안내문 삭제
        drink_options,
        key="drink_radio"
    )
    custom_drink = ""
    if drink_selected == "기타 (직접 입력)":
        custom_drink = st.text_input("주종을 직접 입력해 주세요.", key="custom_drink_input")
    if st.button("주종 선택 완료", key="drink_submit_btn"):
        if drink_selected and (drink_selected != "기타 (직접 입력)" or custom_drink):
            st.session_state.drink = custom_drink if drink_selected == "기타 (직접 입력)" else drink_selected
            st.session_state.step = "ingredient"
            st.rerun()

elif st.session_state.step == "ingredient":
    st.markdown(
        "<span style='font-size:20px;'>선호하는 재료를 선택하세요.</span>",
        unsafe_allow_html=True
    )
    ingredient = st.radio(
        "",  # 안내문은 위에서 처리
        ("고기", "해산물", "채소", "과일", "아무거나"),
        key="ingredient_radio"
    )
    if st.button("재료 선택 완료", key="ingredient_submit_btn"):
        if ingredient:
            st.session_state.ingredient = ingredient
            # 재료 변경 후 바로 recommend로 이동하도록 설정
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
    if st.button("다음(싫어하는 재료)"):
        st.session_state.hate = hate
        st.session_state.step = "digest"
        st.rerun()

elif st.session_state.step == "digest":
    st.markdown(
        "<span style='font-size:20px;'>알레르기, 불내증, 소화 불편감 등 건강상 제한이 있나요?</span>",
        unsafe_allow_html=True
    )
    digest = st.text_input("", placeholder="없으면 비워두세요", key="digest_input")
    if st.button("다음(건강정보)"):
        st.session_state.digest = digest
        st.session_state.step = "recommend"
        st.rerun()

elif st.session_state.step == "calorie_input_again":
    st.markdown(
        "<span style='font-size:20px;'>새로운 최대 칼로리를 숫자로 입력하세요 (예: 350)</span>",
        unsafe_allow_html=True
    )
    new_limit = st.text_input(
        "",  # 안내문은 위에서 처리
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
    with st.spinner("추천 메뉴를 찾는 중입니다..."):
        # 파일 로드
        food_menu_data = load_file_data("food_menu_fixed.csv")
        drink_menu_data = load_file_data("drink_menu.csv")
        
        # 파일 데이터 파싱
        food_menu_df = parse_csv_data(food_menu_data, "food_menu_fixed.csv") if food_menu_data else None
        drink_menu_df = parse_csv_data(drink_menu_data, "drink_menu.csv") if drink_menu_data else None
        
        # 메뉴 필터링
        filtered_menus = []
        drink_recommendations = []
        
        if food_menu_df is not None:
            if st.session_state.ingredient != "아무거나":
                filtered_menus = food_menu_df[food_menu_df["대분류"] == st.session_state.ingredient]["음식명"].tolist()
            else:
                filtered_menus = food_menu_df["음식명"].tolist()
            # 싫어하는 재료/안주 제외
            if st.session_state.hate:
                hate_list = [h.strip() for h in st.session_state.hate.split(",")]
                filtered_menus = [menu for menu in filtered_menus if all(h not in menu for h in hate_list)]
        
        if drink_menu_df is not None:
            drink_recommendations = drink_menu_df[drink_menu_df["주종"] == st.session_state.drink]["추천 안주"].tolist()
        
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = (
            f"당신은 저칼로리 안주 추천 챗봇입니다.\n"
            f"조건:\n"
            f"- 최대 칼로리: {st.session_state.calorie_limit}kcal\n"
            f"- 안주 스타일: {st.session_state.style}\n"
            f"- 주종: {st.session_state.drink}\n"
            f"- 선호 재료: {st.session_state.ingredient}\n"
            f"- 싫어하는 재료/안주: {st.session_state.hate}\n"
            f"- 건강 제한: {st.session_state.digest}\n"
            f"다음 메뉴 목록에서 조건에 맞는 배달 가능한 저칼로리 안주 메뉴 3가지를 추천해 주세요:\n"
            f"{', '.join(filtered_menus) if filtered_menus else '모든 메뉴'}\n"
            f"주종({st.session_state.drink})에 어울리는 추천 안주: {', '.join(drink_recommendations) if drink_recommendations else '없음'}\n"
            f"각 메뉴는 이름, 예상 칼로리, 추천 이유를 포함해 주세요. "
            f"답변은 번호 목록으로 해주세요 (예: 1. 메뉴 이름 - 칼로리 - 추천 이유)."
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 저칼로리 안주 추천 챗봇입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message.content.strip()
        st.session_state.menu_candidates = bot_reply
        st.session_state.step = "show_menu"
        st.rerun()

elif st.session_state.step == "show_menu":
    st.markdown("<span style='font-size:20px;'>**추천 메뉴:**</span>", unsafe_allow_html=True)
    st.markdown(st.session_state.menu_candidates)
    st.markdown("<span style='font-size:20px;'>마음에 드는 번호를 눌러주세요.</span>", unsafe_allow_html=True)
    menu_options = ["1", "2", "3", "마음에 드는 메뉴가 없어요"]
    menu_selection = st.radio("", menu_options, key="menu_selection_radio")
    if st.button("선택 완료"):
        if menu_selection in ["1", "2", "3"]:
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
        ["다른 안주 더보기", "칼로리 올리기", "재료 바꾸기"],
        key="no_menu_choice_radio"
    )
    if st.button("옵션 선택 완료"):
        if no_menu_choice == "다른 안주 더보기":
            st.session_state.step = "recommend"
        elif no_menu_choice == "칼로리 올리기":
            st.session_state.step = "calorie_input_again"
        elif no_menu_choice == "재료 바꾸기":
            st.session_state.from_no_menu_options = True  # 재료 변경 플래그 설정
            st.session_state.ingredient = None
            st.session_state.step = "ingredient"
        st.rerun()

elif st.session_state.step == "location":
    st.markdown(
        "<span style='font-size:20px;'>주변 맛집 찾아드릴게요! 배달 또는 방문할 지역을 입력하세요.</span>",
        unsafe_allow_html=True
    )
    region = st.text_input("", placeholder="예: 왕십리", key="region_input")
    if st.button("위치 안내"):
        if region:
            selected_menu = st.session_state.selected_menu
            # GPT 응답에서 선택된 메뉴 이름 추출
            menu_lines = st.session_state.menu_candidates.split("\n")
            selected_menu_name = None
            for line in menu_lines:
                if line.startswith(f"{selected_menu}."):
                    selected_menu_name = line.split(" - ")[0].replace(f"{selected_menu}. ", "").strip()
                    break
            if selected_menu_name:
                st.markdown(
                    f"<span style='font-size:20px;'>**{region}에서 '{selected_menu_name}' 맛집 검색 결과:**</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"[카카오맵에서 '{region} {selected_menu_name}' 검색](https://map.kakao.com/?q={region}%20{selected_menu_name})")
            else:
                st.markdown(
                    f"<span style='font-size:20px;'>**{region} 맛집 검색 결과:**</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"[카카오맵에서 '{region} 맛집' 검색](https://map.kakao.com/?q={region}%20맛집)")
            if st.button("확인 완료"):
                st.session_state.step = "diet_tip"
                st.rerun()

elif st.session_state.step == "diet_tip":
    st.markdown(
        "<span style='font-size:20px;'>주문이 완료되었습니다! 건강을 위해 간헐적 단식, 조깅, 반신욕 등도 함께 실천해 보세요😊</span>",
        unsafe_allow_html=True
    )
    if st.button("처음으로"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()