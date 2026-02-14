import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. 页面配置 ---
st.set_page_config(page_title="学生全科诊断系统 (Pro Max)", layout="wide", page_icon="🎓")

# ==============================================================================
# ⚙️ 【中央配置区域】
# ==============================================================================

# --- 1. 总成绩表 (用于查总分、排名) ---
# 必须填入两个链接！
SCORE_URL_PHYSICS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyhhA4C2A9hp-2165uyRgqheKfCccT5NN0dp_FOW2Jl8FE4VmAMPajsWKiTEOCcqIxhIDnuIUwOoQ0/pub?gid=0&single=true&output=csv"  # 👈 物理方向总分表 (昨天的物理表)
SCORE_URL_HISTORY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyhhA4C2A9hp-2165uyRgqheKfCccT5NN0dp_FOW2Jl8FE4VmAMPajsWKiTEOCcqIxhIDnuIUwOoQ0/pub?gid=1671669597&single=true&output=csv"  # 👈 历史方向总分表 (昨天的历史表)

# --- 2. 各科深度诊断表 (用于看知识点雷达图) ---
# 格式：三层表头 (题目-知识点-满分)
# 💡 提示：没做好的科目就留空 ""，会自动隐藏
SUBJECT_URLS = {
    # --- 理科 ---
    "⚡ 物理诊断": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLNvn1FqBT1F5w1J7ENAUA3YQuOvfLoohdW4ihjsEZkC_R8JZMCQPqtthzzitC2ZU3mvOMRUmo5omH/pub?gid=761604232&single=true&output=csv",  # 👈 今天的物理详细表
    "🧪 化学诊断": "",
    "🧬 生物诊断": "",
    
    # --- 文科 ---
    "📜 历史诊断": "",
    "🌍 地理诊断": "",
    "⚖️ 政治诊断": "",

    # --- 主科 ---
    "📐 数学诊断": "",
    "📖 语文诊断": "",
    "🔤 英语诊断": ""
}

# ==============================================================================

# --- CSS 美化 ---
st.markdown("""
<style>
    .metric-card { background-color: #f8f9fa; border-left: 5px solid #1f77b4; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.title("🎓 系统导航")
    
    # 1. 先选方向 (恢复了这个关键开关！)
    direction = st.selectbox("请选择分科方向", ["物理方向", "历史方向"])
    
    st.divider()

    # 2. 动态生成功能菜单
    available_menus = ["📑 成绩查询 (总分)"]
    for name, url in SUBJECT_URLS.items():
        if url and url.strip():
            available_menus.append(name)
    
    menu = st.radio("请选择功能：", available_menus)
    
    st.divider()
    
    # 3. 身份验证
    st.markdown("### 🔐 身份验证")
    input_name = st.text_input("学生姓名")
    input_id = st.text_input("考号/学号")

# --- 通用函数 ---
def authenticate(df, name, student_id, id_col_name='考号'):
    df[id_col_name] = df[id_col_name].astype(str).str.strip()
    df['姓名'] = df['姓名'].astype(str).str.strip()
    student = df[(df['姓名'] == name.strip()) & (df[id_col_name] == student_id.strip())]
    return student.iloc[0] if len(student) > 0 else None

def render_subject_analysis(subject_name, url, student_name, student_id):
    st.header(f"{subject_name} - 深度学情报告")
    try:
        df = pd.read_csv(url, header=[0, 1, 2], on_bad_lines='skip')
        # 自动定位列
        name_idx, id_idx = -1, -1
        for i, col in enumerate(df.columns):
            if '姓名' in str(col[0]): name_idx = i
            if '考号' in str(col[0]) or '学号' in str(col[0]): id_idx = i
            
        if name_idx == -1 or id_idx == -1:
            st.error("Excel格式错误：未找到姓名或考号列。")
            return

        # 验证
        all_names = df.iloc[:, name_idx].astype(str).str.strip().values
        all_ids = df.iloc[:, id_idx].astype(str).str.strip().values
        
        found_idx = -1
        for idx, (n, i) in enumerate(zip(all_names, all_ids)):
            if n == student_name.strip() and i == student_id.strip():
                found_idx = idx
                break
        
        if found_idx == -1:
            st.warning(f"未找到 {student_name} 的数据，可能是缺考或未录入。")
            return

        # 分析
        st.success(f"✅ 数据加载成功")
        knowledge_map = {} 
        for col in df.columns:
            q_name, k_point = str(col[0]).strip(), str(col[1]).strip()
            try: full = float(col[2])
            except: full = 0
            if '姓名' in q_name or '考号' in q_name or full <= 0: continue
            
            if k_point not in knowledge_map: knowledge_map[k_point] = {'my': 0, 'full': 0, 'class_total': 0}
            try: my_s = float(df.iloc[found_idx][col])
            except: my_s = 0
            class_s = pd.to_numeric(df[col], errors='coerce').mean()
            knowledge_map[k_point]['my'] += my_s
            knowledge_map[k_point]['full'] += full
            knowledge_map[k_point]['class_total'] += class_s
        
        # 画图
        k_data = []
        for kp, val in knowledge_map.items():
            k_data.append({
                '知识点': kp,
                '我的掌握率': round((val['my']/val['full'])*100, 1) if val['full']>0 else 0,
                '班级平均': round((val['class_total']/val['full'])*100, 1) if val['full']>0 else 0,
                '得分': val['my'], '满分': val['full']
            })
        
        df_kp = pd.DataFrame(k_data)
        if not df_kp.empty:
            c1, c2 = st.columns([1, 1])
            with c1:
                fig = go.Figure()
                cats = df_kp['知识点'].tolist() + [df_kp['知识点'].tolist()[0]]
                mys = df_kp['我的掌握率'].tolist() + [df_kp['我的掌握率'].tolist()[0]]
                avgs = df_kp['班级平均'].tolist() + [df_kp['班级平均'].tolist()[0]]
                fig.add_trace(go.Scatterpolar(r=avgs, theta=cats, fill='toself', name='班级平均', line_color='#cccccc'))
                fig.add_trace(go.Scatterpolar(r=mys, theta=cats, fill='toself', name='我的掌握', line_color='#1f77b4'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("💡 诊断建议")
                weak = df_kp[df_kp['我的掌握率'] < df_kp['班级平均']]
                if not weak.empty:
                    st.error("🚨 **需重点关注的薄弱点：**")
                    for _, row in weak.iterrows():
                        st.write(f"- **{row['知识点']}** (掌握率 {row['我的掌握率']}%)")
                else:
                    st.success("🎉 基础非常扎实！")

    except Exception as e:
        st.error(f"数据读取失败: {e}")

# ==============================================================================
# 主逻辑
# ==============================================================================

if not input_name or not input_id:
    st.info("👈 请先在左侧输入姓名和考号。")
    st.stop()

if menu == "📑 成绩查询 (总分)":
    # 1. 自动判断要读哪个表
    if direction == "物理方向":
        target_url = SCORE_URL_PHYSICS
    else:
        target_url = SCORE_URL_HISTORY
    
    # 2. 读取并展示
    if target_url:
        try:
            df = pd.read_csv(target_url, on_bad_lines='skip')
            student = authenticate(df, input_name, input_id, '考号' if '考号' in df.columns else '学号')
            if student is None:
                st.error(f"❌ 在【{direction}】表中未找到该学生。")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("姓名", student['姓名'])
                c2.metric("方向", direction)
                
                # 智能计算总分
                if '总分' in student:
                    total = student['总分']
                else:
                    exclude = ['姓名', '考号', '学号', '班级', '排名']
                    cols = [c for c in df.columns if c not in exclude and pd.to_numeric(student[c], errors='coerce') >= 0]
                    total = sum([student[c] for c in cols])
                
                c3.metric("全科总分", f"{total}")
                
                st.divider()
                st.subheader("各科得分概览")
                
                exclude_cols = ['姓名', '考号', '学号', '班级', '总分', '班级排名', '年级排名', 'Unnamed', '序号']
                subject_cols = []
                for col in df.columns:
                    if col not in exclude_cols and not str(col).startswith('Unnamed'):
                        if pd.to_numeric(student[col], errors='coerce') >= 0:
                            subject_cols.append(col)
                
                if subject_cols:
                    chart_data = pd.DataFrame({
                        "科目": subject_cols,
                        "得分": [student[c] for c in subject_cols]
                    })
                    fig = px.bar(chart_data, x='科目', y='得分', text_auto=True, color='科目')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("未检测到有效科目成绩。")
        except Exception as e:
            st.error(f"无法读取总分表，请检查链接。错误: {e}")
    else:
        st.warning(f"⚠️ 暂未配置【{direction}】的总分表链接。")

else:
    # 各科诊断 (不分方向，直接读配置的链接)
    target_url = SUBJECT_URLS.get(menu)
    if target_url:
        render_subject_analysis(menu, target_url, input_name, input_id)