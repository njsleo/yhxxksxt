import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # 引入绘图大神
import os

st.set_page_config(page_title="学生全科诊断系统", layout="wide")
st.title('🎓 学生全科能力诊断系统 (全彩可视化版)')

# --- 1. 数据加载 ---
data_file = None
default_file = 'data.xlsx'

with st.sidebar:
    st.header("📂 教师管理")
    uploaded_file = st.file_uploader("更新成绩单", type=["xlsx"])
    if uploaded_file:
        data_file = uploaded_file
    elif os.path.exists(default_file):
        data_file = default_file
        st.success("✅ 已自动加载云端成绩单")

if data_file is None:
    st.warning("请上传 Excel 或在 GitHub 存入 data.xlsx")
    st.stop()

# --- 2. 数据清洗与智能识别 ---
try:
    df = pd.read_excel(data_file)
    df = df.dropna(subset=['姓名']) 
    
    # 排除不需要分析的列
    exclude_cols = [
        '姓名', '学号', '考号', '班级', '学校', '区县', '校名', 
        '总分', '总分赋分', '班级排名', '年级排名', 'Unnamed', '序号'
    ]
    
    # 强制转换数字列，找回“消失的科目”
    subject_cols = []
    for col in df.columns:
        if col not in exclude_cols and not str(col).startswith('Unnamed'):
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].notna().sum() > 0:
                subject_cols.append(col)

    if not subject_cols:
        st.error("未找到有效的科目列！请检查Excel表头。")
        st.stop()

    # --- 3. 班级概况 (升级为彩色柱状图) ---
    st.header("📊 班级整体学科分析")
    
    # 计算全班各科平均分
    class_avg = df[subject_cols].mean().round(1)
    
    # 把数据整理成画图需要的格式
    avg_df = class_avg.reset_index()
    avg_df.columns = ['科目', '平均分'] # 重命名列方便画图

    # 【升级点】：使用 Plotly 画彩色柱状图
    fig_bar = px.bar(
        avg_df, 
        x='科目', 
        y='平均分', 
        color='科目',      # 这行代码让不同科目颜色不同！
        text_auto=True,   # 自动在柱子上显示数字
        title="全班各科平均分对比"
    )
    # 隐藏图例以节省空间（因为X轴已经写了科目名）
    fig_bar.update_layout(showlegend=False) 
    
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 4. 个人“自适应”雷达图 ---
    st.header("🔍 学生个人深度诊断")
    
    # 搜索框
    student_list = df['姓名'].unique().tolist()
    selected_student = st.selectbox("请选择学生姓名：", student_list)
    
    if selected_student:
        student_data = df[df['姓名'] == selected_student].iloc[0]
        
        # 只提取该学生“有分数”的科目
        my_subjects = []
        my_scores = []
        class_scores = []
        
        for sub in subject_cols:
            score = student_data[sub]
            if pd.notna(score) and score > 0:
                my_subjects.append(sub)
                my_scores.append(score)
                class_scores.append(class_avg[sub])
        
        if not my_subjects:
            st.warning("该学生似乎没有有效的单科成绩。")
        else:
            # 数据闭环
            plot_subjects = my_subjects + [my_subjects[0]]
            plot_my_scores = my_scores + [my_scores[0]]
            plot_class_scores = class_scores + [class_scores[0]]
            
            fig = go.Figure()
            
            # 班级平均线
            fig.add_trace(go.Scatterpolar(
                r=plot_class_scores,
                theta=plot_subjects,
                fill='toself',
                name='班级平均',
                line_color='gray',
                opacity=0.3
            ))
            
            # 学生个人线
            fig.add_trace(go.Scatterpolar(
                r=plot_my_scores,
                theta=plot_subjects,
                fill='toself',
                name=f'{selected_student}',
                line_color='#1f77b4'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(max(plot_my_scores), max(plot_class_scores)) + 10])
                ),
                title=f"【{selected_student}】 选考科目能力模型 ({len(my_subjects)}选)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("详细得分：")
            display_df = pd.DataFrame([student_data[my_subjects]])
            st.dataframe(display_df, hide_index=True)

except Exception as e:
    st.error(f"发生错误：{e}")