import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 页面基础设置 ---
st.set_page_config(page_title="学生成绩查询系统", layout="wide")

# ==============================================================================
# 👇👇👇 请在这里填入您的谷歌表格链接 (保留双引号，不要换行) 👇👇👇
# ==============================================================================

# 1. 把您的【物理方向】CSV链接粘贴在下面 (在两个引号中间):
PHYSICS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyhhA4C2A9hp-2165uyRgqheKfCccT5NN0dp_FOW2Jl8FE4VmAMPajsWKiTEOCcqIxhIDnuIUwOoQ0/pub?gid=0&single=true&output=csv" 

# 2. 把您的【历史方向】CSV链接粘贴在下面 (在两个引号中间):
HISTORY_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyhhA4C2A9hp-2165uyRgqheKfCccT5NN0dp_FOW2Jl8FE4VmAMPajsWKiTEOCcqIxhIDnuIUwOoQ0/pub?gid=1671669597&single=true&output=csv" 

# ==============================================================================


# --- 侧边栏：简单说明 ---
with st.sidebar:
    st.header("ℹ️ 系统说明")
    st.info("本系统数据已接入云端，家长可直接查询，无需登录 GitHub。")
    st.markdown("---")
    st.caption("🔒 数据安全保护中")

# --- 主标题 ---
st.title('🎓 学生成绩安全查询系统')
st.markdown("### 请输入信息进行验证查询")

# --- 查询表单区域 ---
with st.form("query_form"):
    # 1. 选择方向
    direction_options = ["物理方向", "历史方向"]
    selected_sheet = st.selectbox("第一步：请选择分科方向", direction_options)
    
    col1, col2 = st.columns(2)
    # 2. 输入姓名
    input_name = col1.text_input("第二步：请输入学生姓名")
    # 3. 输入考号
    input_id = col2.text_input("第三步：请输入考号/学号")
    
    # 提交按钮
    submitted = st.form_submit_button("🔍 立即查询", use_container_width=True)

# --- 核心逻辑 ---
if submitted:
    if not input_name or not input_id:
        st.warning("⚠️ 请完整填写姓名和考号！")
        st.stop()

    # 1. 确定要读哪个链接
    if selected_sheet == '物理方向':
        target_url = PHYSICS_URL
    else:
        target_url = HISTORY_URL

    # 2. 尝试读取数据
    try:
        # 这里的 on_bad_lines='skip' 是为了防止个别坏数据卡死系统
        df = pd.read_csv(target_url, on_bad_lines='skip')
    except Exception as e:
        st.error(f"❌ 无法连接数据源，请检查链接是否正确。错误信息: {e}")
        st.stop()

    # 3. 数据清洗
    try:
        df = df.dropna(subset=['姓名']) # 去除姓名为空的行
        
        # 自动识别考号列 (兼容 '考号' 或 '学号')
        id_col = '考号' if '考号' in df.columns else '学号'
        if id_col not in df.columns:
            st.error("数据表中未找到【考号】或【学号】列！")
            st.stop()
            
        # 强制把考号和姓名转为字符串，并去除空格，防止匹配失败
        df[id_col] = df[id_col].astype(str).str.strip()
        df['姓名'] = df['姓名'].astype(str).str.strip()
        
        # 输入的信息也去除空格
        input_name = input_name.strip()
        input_id = input_id.strip()

        # 4. 执行查询 (姓名和考号必须同时匹配)
        result = df[(df['姓名'] == input_name) & (df[id_col] == input_id)]
        
        if len(result) == 0:
            st.error(f"❌ 查询失败：在【{selected_sheet}】中未找到该学生，请检查方向、姓名或考号是否正确。")
        else:
            st.success(f"✅ 验证通过！正在显示 {input_name} 的成绩报告")
            student_data = result.iloc[0]

            # 5. 智能识别科目列 (自动排除非分数列)
            exclude_cols = ['姓名', '学号', '考号', '班级', '学校', '区县', '校名', '总分', '总分赋分', '班级排名', '年级排名', 'Unnamed', '序号', 'id', 'ID']
            subject_cols = []
            
            for col in df.columns:
                # 排除名单里的列，且排除 Unnamed 开头的列
                if col not in exclude_cols and not str(col).startswith('Unnamed'):
                    # 尝试转为数字
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # 如果这一列有效数字超过0个，就算作科目
                    if df[col].notna().sum() > 0:
                        subject_cols.append(col)
            
            # 计算该方向的平均分
            class_avg = df[subject_cols].mean().round(1)

            # 提取该学生的有效成绩
            my_subjects = []
            my_scores = []
            class_scores = []
            
            for sub in subject_cols:
                score = student_data[sub]
                # 只有分数存在且大于0才显示
                if pd.notna(score) and score >= 0:
                    my_subjects.append(sub)
                    my_scores.append(score)
                    class_scores.append(class_avg[sub])
            
            if not my_subjects:
                st.warning("该学生没有有效成绩数据。")
            else:
                total_score = sum(my_scores)
                
                # --- 展示模块 1: 成绩卡片 ---
                st.markdown("### 📄 成绩概览")
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("姓名", input_name)
                kpi2.metric("方向", selected_sheet)
                kpi3.metric("总分", f"{total_score:.1f}")

                st.divider()

                # --- 展示模块 2: 图表与明细 ---
                col_chart, col_table = st.columns([1, 1])
                
                with col_chart:
                    st.markdown("**📊 能力雷达图**")
                    # 数据闭环 (为了画封闭的雷达图)
                    plot_subjects = my_subjects + [my_subjects[0]]
                    plot_my_scores = my_scores + [my_scores[0]]
                    plot_class_scores = class_scores + [class_scores[0]]
                    
                    fig = go.Figure()
                    # 画班级平均
                    fig.add_trace(go.Scatterpolar(
                        r=plot_class_scores, theta=plot_subjects, fill='toself',
                        name='方向平均', line_color='#cccccc', opacity=0.4
                    ))
                    # 画个人成绩
                    fig.add_trace(go.Scatterpolar(
                        r=plot_my_scores, theta=plot_subjects, fill='toself',
                        name='我的成绩', line_color='#1f77b4'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, max(max(plot_my_scores), max(plot_class_scores)) + 10])),
                        margin=dict(t=20, b=20, l=20, r=20),
                        height=350,
                        legend=dict(orientation="h", y=-0.1)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col_table:
                    st.markdown("**📝 单科得分明细**")
                    # 构造表格数据
                    score_data = []
                    for sub, score, avg in zip(my_subjects, my_scores, class_scores):
                        status = "🟢" if score >= avg else "🔴"
                        score_data.append({
                            "科目": sub,
                            "我的分数": score,
                            "方向平均": avg,
                            "对比": status
                        })
                    st.dataframe(pd.DataFrame(score_data), hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"数据处理出错: {e}")
