import streamlit as st
from streamlit_elements import elements, mui, dashboard
import uuid

# --- 1. 앱 기본 설정 ---
st.set_page_config(page_title="알고리즘 순서도 메이커", layout="wide")
st.title("🎨 알고리즘 순서도 메이커")
st.markdown("왼쪽 사이드바에서 블록을 추가하고, 캔버스 위에서 자유롭게 배치, 편집, 삭제해 보세요!")

# --- 2. 세션 상태(Session State) 초기화 ---
if 'blocks' not in st.session_state:
    st.session_state.blocks = [
        {"id": str(uuid.uuid4()), "name": "시작", "type": "start_end", "content": "알고리즘 시작", "layout": {"x": 2, "y": 0, "w": 2, "h": 1}},
        {"id": str(uuid.uuid4()), "name": "입력", "type": "io", "content": "점수를 입력받는다", "layout": {"x": 1, "y": 1, "w": 4, "h": 2}},
        {"id": str(uuid.uuid4()), "name": "조건", "type": "decision", "content": "점수가 90점 이상인가?", "layout": {"x": 1, "y": 3, "w": 4, "h": 3}},
        {"id": str(uuid.uuid4()), "name": "출력", "type": "io", "content": "'합격'을 출력한다", "layout": {"x": 1, "y": 6, "w": 4, "h": 2}},
        {"id": str(uuid.uuid4()), "name": "끝", "type": "start_end", "content": "알고리즘 종료", "layout": {"x": 2, "y": 8, "w": 2, "h": 1}},
    ]

# 각 순서도 블록 유형에 맞는 스타일 정의
BLOCK_STYLES = {
    "start_end": {"backgroundColor": "#FFADAD", "borderRadius": "25px", "textAlign": "center"},
    "process": {"backgroundColor": "#CAFFBF", "textAlign": "center"},
    "io": {"backgroundColor": "#A0C4FF", "textAlign": "center"},
    "decision": {"backgroundColor": "#FDFFB6", "clipPath": "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)", "textAlign": "center", "paddingTop": "25%"},
    "loop": {"backgroundColor": "#FFD6A5", "textAlign": "center"},
}

# --- 3. 핵심 기능 함수 정의 ---

def add_block(block_type, name):
    """새로운 순서도 블록을 추가하는 함수"""
    new_block = {
        "id": str(uuid.uuid4()), "name": name, "type": block_type,
        "content": f"{name} 내용을 입력하세요.",
        "layout": {"x": 0, "y": 0, "w": 3, "h": 2}
    }
    st.session_state.blocks.append(new_block)

def update_block_content(block_id, new_content):
    """블록 내용 업데이트 함수"""
    for block in st.session_state.blocks:
        if block['id'] == block_id:
            block['content'] = new_content
            break

def delete_block(block_id):
    """블록 삭제 함수"""
    st.session_state.blocks = [b for b in st.session_state.blocks if b['id'] != block_id]

# --- 4. UI 화면 그리기 ---

# 사이드바: 컨트롤 패널
with st.sidebar:
    st.header("⚙️ 컨트롤 패널")
    st.subheader("1. 블록 추가")
    st.button("시작 / 끝", on_click=add_block, args=("start_end", "시작/끝"), use_container_width=True)
    st.button("처리 (계산, 변수)", on_click=add_block, args=("process", "처리"), use_container_width=True)
    st.button("입력 / 출력", on_click=add_block, args=("io", "입력/출력"), use_container_width=True)
    st.button("조건 (판단)", on_click=add_block, args=("decision", "조건"), use_container_width=True)
    st.button("반복", on_click=add_block, args=("loop", "반복"), use_container_width=True)

    st.divider()
    st.subheader("2. 캔버스 관리")
    if st.button("모두 삭제", type="primary", use_container_width=True):
        st.session_state.blocks = []
        st.rerun()

    st.divider()
    # [수정됨] 자동 캡쳐 버튼 대신, 컴퓨터 기본 캡쳐 기능 사용 안내
    st.subheader("3. 결과 제출 방법")
    st.info(
        """
        순서도를 완성한 후, 컴퓨터의 스크린샷(화면 캡쳐) 기능을 사용하여 이미지를 저장하고 제출하세요.

        - **윈도우:** `Win` + `Shift` + `S`
        - **Mac:** `Cmd` + `Shift` + `4`
        """
    )

# 메인 화면: 순서도를 그리는 캔버스
layout = [dashboard.Item(b['id'], **b['layout']) for b in st.session_state.blocks]

with elements("flowchart_canvas"):
    with dashboard.Grid(
        layout,
        draggableHandle=".draggable-handle",
        on_change=lambda new_layout: [
            setattr(block, 'layout', next(item for item in new_layout if item.i == block.id))
            for block in st.session_state.blocks
        ]
    ):
        for block in st.session_state.blocks:
            with mui.Card(key=block['id'], sx={"display": "flex", "flexDirection": "column", "height": "100%", **BLOCK_STYLES[block['type']]}, elevation=3):
                with mui.CardHeader(
                    className="draggable-handle",
                    title=block['name'],
                    action=mui.IconButton(mui.icon.Delete, onClick=lambda _, bid=block['id']: delete_block(bid)),
                    sx={"backgroundColor": "rgba(240, 242, 246, 0.8)", "padding": "5px 15px", "cursor": "move"},
                ):
                    pass
                with mui.CardContent(sx={"flex": 1, "padding": "10px"}):
                    mui.TextField(
                        label="내용 입력",
                        defaultValue=block['content'],
                        variant="outlined",
                        fullWidth=True,
                        multiline=True,
                        rows=2,
                        onChange=(lambda e, bid=block['id']: update_block_content(bid, e.target.value)),
                        sx={"height": "100%"}
                    )