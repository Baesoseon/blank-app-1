import streamlit as st
from streamlit_elements import elements, mui, dashboard
from streamlit_mermaid import st_mermaid
import uuid
import re # 정규표현식 라이브러리 import

# --- 1. 앱 기본 설정 ---
st.set_page_config(page_title="알고리즘 순서도 메이커", layout="wide")
st.title("🎨 알고리즘 순서도 메이커 (오류 수정)")
st.info("이제 Graphviz 없이, 문법 오류 없이 순서도를 만들 수 있습니다!")

# --- 2. 세션 상태(Session State) 초기화 ---
# [수정됨] Mermaid에서 안전하게 사용 가능한 영문/숫자 ID로 변경
if 'blocks' not in st.session_state:
    st.session_state.blocks = [
        {"id": "Start", "name": "시작", "type": "start_end", "content": "게임 시작", "layout": {"x": 4, "y": 0, "w": 2, "h": 1}},
        {"id": "Process1", "name": "처리", "type": "process", "content": "정답 숫자(예:7)를 정한다", "layout": {"x": 2, "y": 1, "w": 6, "h": 2}},
        {"id": "Input1", "name": "입력", "type": "io", "content": "추측 숫자를 입력받는다", "layout": {"x": 2, "y": 3, "w": 6, "h": 2}},
        {"id": "Decision1", "name": "조건", "type": "decision", "content": "추측 숫자가 정답과 같은가?", "layout": {"x": 2, "y": 5, "w": 6, "h": 3}},
        {"id": "OutputWin", "name": "출력", "type": "io", "content": "'정답!'을 출력한다", "layout": {"x": 0, "y": 8, "w": 4, "h": 2}},
        {"id": "OutputRetry", "name": "출력", "type": "io", "content": "'다시!'를 출력한다", "layout": {"x": 6, "y": 8, "w": 4, "h": 2}},
        {"id": "End", "name": "끝", "type": "start_end", "content": "게임 종료", "layout": {"x": 4, "y": 10, "w": 2, "h": 1}},
    ]
if 'connections' not in st.session_state:
    st.session_state.connections = [
        {"from": "Start", "to": "Process1", "label": ""},
        {"from": "Process1", "to": "Input1", "label": ""},
        {"from": "Input1", "to": "Decision1", "label": ""},
        {"from": "Decision1", "to": "OutputWin", "label": "참(Yes)"},
        {"from": "Decision1", "to": "OutputRetry", "label": "거짓(No)"},
        {"from": "OutputWin", "to": "End", "label": ""},
        {"from": "OutputRetry", "to": "Input1", "label": ""}, # 반복 구조
    ]

# Mermaid 문법에 맞는 블록 모양 및 스타일 클래스 정의
BLOCK_STYLES = {
    "start_end": {"shape_open": "(", "shape_close": ")", "class": "startEndStyle"},
    "process": {"shape_open": "[", "shape_close": "]", "class": "processStyle"},
    "io": {"shape_open": "[/", "shape_close": "\\]", "class": "ioStyle"},
    "decision": {"shape_open": "{", "shape_close": "}", "class": "decisionStyle"},
}

# --- 3. 핵심 기능 함수 정의 ---
def create_safe_id(name):
    """Mermaid에서 사용할 안전한 영문/숫자 ID를 생성하는 함수"""
    # 영문 타입 이름과 고유 번호를 조합하여 ID 생성
    safe_name = re.sub(r'[^a-zA-Z]', '', name) # 한글, 특수문자 제거
    return f"{safe_name}{str(uuid.uuid4())[:4]}"

def add_block(block_type, name):
    new_id = create_safe_id(block_type)
    new_block = { "id": new_id, "name": name, "type": block_type, "content": f"{name} 내용을 입력.", "layout": {"x": 0, "y": 0, "w": 4, "h": 2} }
    st.session_state.blocks.append(new_block)

# (update_block_content, delete_block, add_connection, delete_connection 함수는 이전과 동일)
def update_block_content(block_id, new_content):
    for block in st.session_state.blocks:
        if block['id'] == block_id:
            block['content'] = new_content; break
def delete_block(block_id):
    st.session_state.blocks = [b for b in st.session_state.blocks if b['id'] != block_id]
    st.session_state.connections = [c for c in st.session_state.connections if c['from'] != block_id and c['to'] != block_id]
def add_connection(from_node, to_node, label=""):
    if from_node and to_node and from_node != to_node:
        new_connection = {"from": from_node, "to": to_node, "label": label}
        for conn in st.session_state.connections:
            if conn['from'] == from_node and conn['label'] == label and label:
                st.warning(f"'{from_node}' 블록의 '{label}' 경로는 이미 연결되어 있습니다."); return
        st.session_state.connections.append(new_connection)
def delete_connection(conn_to_delete):
    st.session_state.connections.remove(conn_to_delete)

# --- 4. UI 화면 그리기 ---
# (사이드바 UI는 이전과 동일)
with st.sidebar:
    st.header("⚙️ 컨트롤 패널")
    st.subheader("1. 블록 추가")
    col1, col2 = st.columns(2)
    col1.button("시작/끝", on_click=add_block, args=("start_end", "시작/끝"), use_container_width=True)
    col2.button("입력/출력", on_click=add_block, args=("io", "입력/출력"), use_container_width=True)
    col1.button("처리", on_click=add_block, args=("process", "처리"), use_container_width=True)
    col2.button("조건", on_click=add_block, args=("decision", "조건"), use_container_width=True)

    st.divider()
    st.subheader("2. 화살표 연결")
    if len(st.session_state.blocks) >= 1:
        block_map = {b['id']: f"{b['name']} ({b['id']})" for b in st.session_state.blocks}
        from_node_id = st.selectbox("시작 블록:", options=block_map.keys(), format_func=lambda x: block_map.get(x, "선택"))
        from_node_type = next((b['type'] for b in st.session_state.blocks if b['id'] == from_node_id), None)

        if from_node_type == 'decision':
            st.write("---"); st.markdown("**조건 블록 연결 (선택 구조)**")
            to_node_yes_id = st.selectbox("`참(Yes)`일 때 도착 블록:", options=block_map.keys(), format_func=lambda x: block_map.get(x, "선택"), key="yes_node")
            st.button("✅ 참일 때 연결 추가", on_click=add_connection, args=(from_node_id, to_node_yes_id, "참(Yes)"), use_container_width=True)
            to_node_no_id = st.selectbox("`거짓(No)`일 때 도착 블록:", options=block_map.keys(), format_func=lambda x: block_map.get(x, "선택"), key="no_node")
            st.button("❌ 거짓일 때 연결 추가", on_click=add_connection, args=(from_node_id, to_node_no_id, "거짓(No)"), use_container_width=True)
            st.write("---")
        else:
            to_node_id = st.selectbox("도착 블록:", options=block_map.keys(), format_func=lambda x: block_map.get(x, "선택"))
            st.button("🔗 연결 추가", on_click=add_connection, args=(from_node_id, to_node_id, ""), use_container_width=True)
    else:
        st.info("블록을 1개 이상 추가해야 연결할 수 있습니다.")

    if st.session_state.connections:
        st.write("현재 연결 목록:")
        for conn in st.session_state.connections:
            label_text = f" [{conn['label']}]" if conn['label'] else ""
            st.button(f"'{block_map.get(conn['from'])}' → '{block_map.get(conn['to'])}'{label_text} (삭제)", 
                      key=f"del_{conn['from']}{conn['to']}{conn['label']}", on_click=delete_connection, args=(conn,))

    st.divider()
    if st.button("모두 삭제", type="primary", use_container_width=True):
        st.session_state.blocks, st.session_state.connections = [], []; st.rerun()

# (메인 편집 캔버스 UI는 이전과 동일)
st.subheader("📋 편집 캔버스 (블록 배치 및 내용 수정)")
layout = [dashboard.Item(b['id'], **b['layout']) for b in st.session_state.blocks]
with elements("flowchart_canvas"):
    with dashboard.Grid(layout, on_change=lambda new_layout: [setattr(b, 'layout', next(i for i in new_layout if i.i == b.id)) for b in st.session_state.blocks]):
        for block in st.session_state.blocks:
            with mui.Card(key=block['id'], sx={"display": "flex", "flexDirection": "column", "height": "100%", "cursor": "move", "textAlign": "center"}, elevation=3):
                mui.CardHeader(title=block['name'], action=mui.IconButton(mui.icon.Delete, onClick=lambda _, bid=block['id']: delete_block(bid)),
                               sx={"backgroundColor": "rgba(240, 242, 246, 0.8)", "padding": "5px 15px"})
                with mui.CardContent(sx={"flex": 1, "padding": "10px"}):
                    mui.TextField(defaultValue=block['content'], variant="outlined", fullWidth=True, multiline=True, rows=2,
                                  onChange=(lambda e, bid=block['id']: update_block_content(bid, e.target.value)), sx={"height": "100%"})

# --- [핵심 수정] 최종 순서도 렌더링 (Mermaid 문법 수정) ---
st.divider()
st.subheader("📊 최종 순서도 (화살표 포함)")

if st.session_state.blocks:
    mermaid_code = "graph TD\n" # TD: Top to Down (위에서 아래로)
    
    # 1. 블록(노드)과 클래스 할당을 정의합니다. (예: Start("게임 시작"):::startEndStyle)
    for block in st.session_state.blocks:
        content = block['content'].replace('"', '&quot;') # 텍스트 안의 따옴표 처리
        style = BLOCK_STYLES[block['type']]
        mermaid_code += f'    {block["id"]}{style["shape_open"]}"{content}"{style["shape_close"]}:::{style["class"]}\n'
        
    # 2. 연결(화살표)을 정의합니다.
    for conn in st.session_state.connections:
        if conn['label']:
            mermaid_code += f'    {conn["from"]} -- "{conn["label"]}" --> {conn["to"]}\n'
        else:
            mermaid_code += f'    {conn["from"]} --> {conn["to"]}\n'
            
    # 3. 각 클래스의 실제 스타일(색상 등)을 정의합니다. (예: classDef startEndStyle fill:#FFADAD)
    mermaid_code += "    classDef startEndStyle fill:#FFADAD,stroke:#333,stroke-width:2px\n"
    mermaid_code += "    classDef processStyle fill:#CAFFBF,stroke:#333,stroke-width:2px\n"
    mermaid_code += "    classDef ioStyle fill:#A0C4FF,stroke:#333,stroke-width:2px\n"
    mermaid_code += "    classDef decisionStyle fill:#FDFFB6,stroke:#333,stroke-width:2px\n"
    
    st_mermaid(mermaid_code, height="600px")
else:
    st.warning("표시할 블록이 없습니다. 사이드바에서 블록을 추가해 주세요.")