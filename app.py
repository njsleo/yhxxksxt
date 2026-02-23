import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# --- 1. 页面配置 (必须在第一行) ---
# initial_sidebar_state="collapsed" 默认收起侧边栏，因为我们现在用顶部导航了！
st.set_page_config(page_title="星辰学情管理系统", layout="wide", page_icon="🏫", initial_sidebar_state="collapsed")

# ==============================================================================
# ⚙️ 【配置区域】
# ==============================================================================
ADMIN_PASSWORD = "123" # 管理员密码

# 1. 总分表链接
SCORE_URL_PHYSICS = "https://docs.google.com/spreadsheets/d/e/2PACX-1v......"
SCORE_URL_HISTORY = "https://docs.google.com/spreadsheets/d/e/2PACX-1v......"

# 2. 详细分析表链接
SUBJECT_URLS = {
    "⚡ 物理": "https://docs.google.com/spreadsheets/d/e/2PACX-1v......",
    "🧪 化学": "", "🧬 生物": "", "📜 历史": "", "🌍 地理": "", "⚖️ 政治": "",
    "📐 数学": "", "📖 语文": "", "🔤 英语": ""
}
# ==============================================================================

# --- 初始化 Session 状态 (核心记忆功能) ---
if 'logged_in_student' not in st.session_state:
    st.session_state.logged_in_student = None
if 'logged_in_direction' not in st.session_state:
    st.session_state.logged_in_direction = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# 退出登录函数
def logout():
    st.session_state.logged_in_student = None
    st.session_state.logged_in_direction = None
    st.session_state.is_admin = False
    st.rerun()

# --- 2. 极致美化 CSS ---
st.markdown("""
<style>
    /* 隐藏 Streamlit 默认的顶部红线、菜单和底部水印，更加清爽 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 调整主体内容距离顶部的距离，适配固定导航栏 */
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 2rem !important;
    }

    /* 全局柔和背景色 */
    .stApp { background-color: #f4f7f9; }

    /* 数据指标卡片美化 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border: 1px solid #ebeef5;
        text-align: center;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0,0,0,0.08); }
    
    /* 表单与卡片容器美化 */
    div[data-testid="stForm"], .custom-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: none;
    }
    
    /* 按钮美化 */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0068C9; color: white; font-weight: bold; border-radius: 8px; border: none; padding: 10px 0;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { background-color: #0052a3; box-shadow: 0 4px 12px rgba(0, 104, 201, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- 3. 🌟 顶端固定导航栏 🌟 ---
# 这里的 CSS 魔术 "position": "sticky", "top": "0" 让它永远固定在顶部！
selected_nav = option_menu(
    menu_title=None, 
    options=["成绩总览", "深度诊断", "教师后台"], 
    icons=["clipboard-data", "bullseye", "person-badge"], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#ffffff", "border-radius": "12px", "box-shadow": "0 4px 15px rgba(0,0,0,0.08)", "margin-bottom": "30px", "position": "sticky", "top": "15px", "z-index": "9999"},
        "icon": {"color": "#888", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "border-radius": "8px", "color": "#555", "font-weight": "600"},
        "nav-link-selected": {"background-color": "#0068C9", "color": "white", "font-weight": "bold"},
    }
)

# --- 核心函数 ---
@st.cache_data(ttl=600)
def load_data(url, header_lines=0):
    try: return pd.read_csv(url, header=header_lines, on_bad_lines='skip')
    except: return None

# ==============================================================================
# 🚀 页面 1 & 2: 学生端逻辑 (居中登录与状态保持)
# ==============================================================================
if selected_nav in ["成绩总览", "深度诊断"]:
    
    # 【未登录】展示居中的精致登录框
    if not st.session_state.logged_in_student:
        col1, col2, col3 = st.columns([1, 1.5, 1]) # 中间略宽，两边留白
        with col2:
            st.markdown("<br><h2 style='text-align: center; color: #333;'>👨‍🎓 欢迎登录系统</h2><br>", unsafe_allow_html=True)
            with st.form("student_login"):
                direction = st.selectbox("📝 选择方向", ["物理方向", "历史方向"])
                name = st.text_input("👤 学生姓名", placeholder="请输入真实姓名")
                stu_id = st.text_input("🔢 考号/学号", placeholder="请输入准确考号")
                
                if st.form_submit_button("🔍 立即查询", use_container_width=True):
                    if name and stu_id:
                        # 保存登录状态
                        st.session_state.logged_in_student = name.strip()
                        st.session_state.logged_in_id = stu_id.strip()
                        st.session_state.logged_in_direction = direction
                        st.rerun() # 瞬间刷新页面，进入系统
                    else:
                        st.error("⚠️ 请完整填写姓名和考号")
    
    # 【已登录】展示内容
    else:
        # 右上角显示用户信息和退出按钮
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**当前用户：** {st.session_state.logged_in_student} | **方向：** {st.session_state.logged_in_direction}")
        with c2:
            if st.button("🚪 退出登录", use_container_width=True): logout()
            
        st.divider()

        target_url = SCORE_URL_PHYSICS if st.session_state.logged_in_direction == "物理方向" else SCORE_URL_HISTORY
        
        # --- 页面1: 成绩总览 ---
        if selected_nav == "成绩总览":
            df = load_data(target_url)
            if df is not None:
                # 兼容学号/考号列名
                id_col = '考号' if '考号' in df.columns else '学号'
                df[id_col] = df[id_col].astype(str).str.strip()
                student = df[(df['姓名'].astype(str).str.strip() == st.session_state.logged_in_student) & 
                             (df[id_col] == st.session_state.logged_in_id)]
                
                if len(student) == 0:
                    st.error("❌ 数据库中未匹配到您的成绩信息，请核对信息或联系老师。")
                else:
                    stu_data = student.iloc[0]
                    # 顶部数据卡片
                    st.markdown("### 🏆 本次考试概览")
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("姓名", stu_data['姓名'])
                    k2.metric("方向", st.session_state.logged_in_direction)
                    
                    # 智能计算总分
                    if '总分' in stu_data: total = stu_data['总分']
                    else:
                        exclude = ['姓名', '考号', '学号', '班级', '排名', '总分', '班级排名', '年级排名']
                        cols = [c for c in df.columns if c not in exclude and pd.to_numeric(stu_data[c], errors='coerce') >= 0]
                        total = sum([stu_data[c] for c in cols])
                        
                    k3.metric("考试总分", f"{total}")
                    k4.metric("班级排名", stu_data.get('班级排名', 'N/A'))
                    
                    st.markdown("<br>### 📊 各科得分雷达与柱状对比", unsafe_allow_html=True)
                    # 图表区域
                    exclude_cols = ['姓名', '考号', '学号', '班级', '总分', '班级排名', '年级排名', 'Unnamed', '序号']
                    subject_cols = [c for c in df.columns if c not in exclude_cols and not str(c).startswith('Unnamed') and pd.to_numeric(stu_data[c], errors='coerce') >= 0]
                    
                    if subject_cols:
                        chart_data = pd.DataFrame({"科目": subject_cols, "得分": [stu_data[c] for c in subject_cols]})
                        col_bar, col_radar = st.columns(2)
                        with col_bar:
                            fig1 = px.bar(chart_data, x='科目', y='得分', text_auto=True, color='科目', title="单科绝对得分")
                            fig1.update_layout(showlegend=False, margin=dict(t=40, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig1, use_container_width=True)
                        with col_radar:
                            fig2 = px.line_polar(chart_data, r='得分', theta='科目', line_close=True, title="学科均衡雷达图")
                            fig2.update_traces(fill='toself', line_color='#0068C9')
                            fig2.update_layout(margin=dict(t=40, b=20, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("总成绩数据未准备好。")
                
        # --- 页面2: 深度诊断 ---
        elif selected_nav == "深度诊断":
            st.markdown("### 🎯 学科知识点深度剖析")
            # 过滤出已经配置链接的科目
            avail_subs = {k: v for k, v in SUBJECT_URLS.items() if v and v.strip()}
            if not avail_subs:
                st.info("老师暂时还未配置单科诊断数据源。")
            else:
                sel_sub = st.selectbox("👇 请选择需要查阅的科目报告", list(avail_subs.keys()))
                diag_url = avail_subs[sel_sub]
                
                df_diag = load_data(diag_url, header_lines=[0, 1, 2])
                if df_diag is not None:
                    # 获取表头层级
                    name_idx, id_idx = -1, -1
                    for i, col in enumerate(df_diag.columns):
                        if '姓名' in str(col[0]): name_idx = i
                        if '考号' in str(col[0]) or '学号' in str(col[0]): id_idx = i
                    
                    all_names = df_diag.iloc[:, name_idx].astype(str).str.strip().values
                    all_ids = df_diag.iloc[:, id_idx].astype(str).str.strip().values
                    
                    found_idx = -1
                    for idx, (n, i) in enumerate(zip(all_names, all_ids)):
                        if n == st.session_state.logged_in_student and i == st.session_state.logged_in_id:
                            found_idx = idx
                            break
                    
                    if found_idx == -1:
                        st.warning(f"在 {sel_sub} 中未找到您的试卷数据。")
                    else:
                        knowledge_map = {} 
                        for col in df_diag.columns:
                            q_name, k_point = str(col[0]).strip(), str(col[1]).strip()
                            try: full = float(col[2])
                            except: full = 0
                            if '姓名' in q_name or '考号' in q_name or full <= 0: continue
                            
                            if k_point not in knowledge_map: knowledge_map[k_point] = {'my': 0, 'full': 0, 'class_total': 0}
                            try: my_s = float(df_diag.iloc[found_idx][col])
                            except: my_s = 0
                            class_s = pd.to_numeric(df_diag[col], errors='coerce').mean()
                            
                            knowledge_map[k_point]['my'] += my_s
                            knowledge_map[k_point]['full'] += full
                            knowledge_map[k_point]['class_total'] += class_s
                        
                        k_data = []
                        for kp, val in knowledge_map.items():
                            k_data.append({
                                '知识点': kp,
                                '我的掌握率': round((val['my']/val['full'])*100, 1) if val['full']>0 else 0,
                                '班级平均': round((val['class_total']/val['full'])*100, 1) if val['full']>0 else 0,
                            })
                        
                        df_kp = pd.DataFrame(k_data)
                        if not df_kp.empty:
                            c_chart, c_text = st.columns([1.2, 1])
                            with c_chart:
                                fig = go.Figure()
                                cats = df_kp['知识点'].tolist() + [df_kp['知识点'].tolist()[0]]
                                mys = df_kp['我的掌握率'].tolist() + [df_kp['我的掌握率'].tolist()[0]]
                                avgs = df_kp['班级平均'].tolist() + [df_kp['班级平均'].tolist()[0]]
                                fig.add_trace(go.Scatterpolar(r=avgs, theta=cats, fill='toself', name='班级平均', line_color='#cccccc'))
                                fig.add_trace(go.Scatterpolar(r=mys, theta=cats, fill='toself', name='我的掌握', line_color='#FF4B4B'))
                                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20))
                                st.plotly_chart(fig, use_container_width=True)
                            with c_text:
                                st.markdown("#### 🩺 专家系统诊断建议")
                                weak = df_kp[df_kp['我的掌握率'] < df_kp['班级平均']]
                                if not weak.empty:
                                    st.error("🚨 **以下知识模块出现明显丢分，需针对性突破：**")
                                    for _, row in weak.iterrows():
                                        diff = row['班级平均'] - row['我的掌握率']
                                        st.write(f"▪ **{row['知识点']}** (落后平均 {diff:.1f}%)")
                                else:
                                    st.success("🎉 **太棒了！** \n\n您在该科目的所有考核知识点均达到或超过班级平均水平，基本功非常扎实，请继续保持！")
                else:
                    st.error("数据表读取异常。")

# ==============================================================================
# 🚀 页面 3: 教师后台 (管理员模式)
# ==============================================================================
elif selected_nav == "教师后台":
    
    if not st.session_state.is_admin:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<br><h2 style='text-align: center; color: #333;'>👨‍🏫 教务管理中枢</h2><br>", unsafe_allow_html=True)
            with st.form("admin_login"):
                pwd = st.text_input("🔐 管理员密码", type="password", placeholder="请输入高级权限密码")
                if st.form_submit_button("验证进入", use_container_width=True):
                    if pwd == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error("密码错误，访问被拒绝。")
    
    else:
        # 已登录管理员
        c1, c2 = st.columns([5, 1])
        c1.markdown("### ⚙️ 管理员控制台")
        if c2.button("退出后台", use_container_width=True): logout()
        
        adm_menu = st.radio("系统功能：", ["🏆 班级成绩PK", "📈 学情总览", "🧠 共性诊断"], horizontal=True)
        st.divider()
        
        adm_direction = st.selectbox("分析方向", ["物理方向", "历史方向"])
        target_url = SCORE_URL_PHYSICS if adm_direction == "物理方向" else SCORE_URL_HISTORY
        
        if adm_menu == "🏆 班级成绩PK":
            df = load_data(target_url)
            if df is not None and '班级' in df.columns:
                exclude = ['姓名', '考号', '学号', '班级', '排名', '总分', '班级排名', '年级排名']
                subjects = [c for c in df.columns if c not in exclude and pd.to_numeric(df[c], errors='coerce').notna().all()]
                class_avg = df.groupby('班级')[subjects + ['总分']].mean().round(1).reset_index()
                
                c_a, c_b = st.columns(2)
                with c_a:
                    fig_total = px.bar(class_avg, x='班级', y='总分', color='班级', text_auto=True, title="各班总分均分对照")
                    fig_total.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_total, use_container_width=True)
                with c_b:
                    sel_sub = st.selectbox("切换单科视角", subjects)
                    fig_sub = px.bar(class_avg, x='班级', y=sel_sub, color='班级', text_auto=True, title=f"各班 {sel_sub} 均分")
                    fig_sub.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_sub, use_container_width=True)

        elif adm_menu == "📈 学情总览":
            df = load_data(target_url)
            if df is not None and '总分' in df.columns:
                m1, m2, m3 = st.columns(3)
                m1.metric("参考总人数", len(df))
                m2.metric("年级均分", round(df['总分'].mean(), 1))
                m3.metric("最高分", df['总分'].max())
                
                fig_hist = px.histogram(df, x="总分", nbins=15, title="总分正态分布情况", color_discrete_sequence=['#0068C9'])
                st.plotly_chart(fig_hist, use_container_width=True)

        elif adm_menu == "🧠 共性诊断":
            avail_subs = [k for k, v in SUBJECT_URLS.items() if v]
            sel_diagnosis = st.selectbox("选择要分析的学科", avail_subs)
            if sel_diagnosis:
                df_diag = load_data(SUBJECT_URLS[sel_diagnosis], header_lines=[0, 1, 2])
                if df_diag is not None:
                    k_stats = {}
                    for col in df_diag.columns:
                        q_name, k_point = str(col[0]).strip(), str(col[1]).strip()
                        try: full = float(col[2])
                        except: full = 0
                        if full <= 0 or '姓名' in q_name: continue
                        if k_point not in k_stats: k_stats[k_point] = []
                        k_stats[k_point].append(pd.to_numeric(df_diag[col], errors='coerce').mean() / full)
                    
                    k_final = [{"知识点": kp, "年级平均掌握率": round(sum(rates)/len(rates)*100, 1)} for kp, rates in k_stats.items()]
                    df_k = pd.DataFrame(k_final).sort_values("年级平均掌握率")
                    
                    fig_k = px.bar(df_k, x="年级平均掌握率", y="知识点", orientation='h', title=f"全校【{sel_diagnosis}】薄弱点扫描", color="年级平均掌握率", color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig_k, use_container_width=True)