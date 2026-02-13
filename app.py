import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="学生全科诊断系统", layout="wide")
st.title('🎓 学生全科能力诊断系统 (Pro版)')

# --- 1. 数据加载 ---
data_file = None
default_file = 'data.xlsx'

with st.sidebar:
    st.header("📂 教师管理后台")
    uploaded_file = st.file_uploader("更新成绩单", type=["xlsx"])
    if uploaded_file:
        data_file = uploaded_file
    elif os.path.exists(default_file):
        data_file = default_file
        st.success("✅ 云端数据已加载")

if data_file is None:
    st.warning("请上传 Excel 或在 GitHub 存入 data.xlsx")
    st.stop()

# --- 2. 智能数据清洗 ---
try:
    df = pd.read_excel(data_file)
    df = df.dropna(subset=['姓名']) 
    
    # 排除非科目列
    exclude_cols = [
        '姓名', '学号', '考号', '班级', '学校', '区县', '校名', 
        '总分', '总分赋分', '班级排名', '年级排名', 'Unnamed', '序号'
    ]
    
    subject_cols = []
    for col in df.columns:
        if col not in exclude_cols and not str(col).startswith('Unnamed'):
            # 强制转数字，非数字变NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # 如果这一列有数字，就算作科目
            if df[col].notna().sum() > 0:
                subject_cols.append(col)

    if not subject_cols:
        st.error("未找到科目列！")
        st.stop()

    # --- 3. 班级概况 (彩虹柱状图) ---
    st.header("📊 班级整体考情")
    
    # 计算平均分
    class_avg = df[subject_cols].mean().round(1)
    
    # 转换数据格式用于画图
    avg_df = class_avg.reset_index()
    avg_df.columns = ['科目', '平均分']
    
    # 使用 Plotly Express 画彩色图
    fig_bar = px.bar(
        avg_df, 
        x='科目', 
        y='平均分', 
        color='科目',  # 【关键】这就让不同科目颜色不一样了
        text_auto=True, 
        title="全班各科平均分概览"
    )
    fig_bar.update_layout(showlegend=False) # 隐藏图例让画面更干净
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 4. 个人精致查分 ---
    st.header("🔍 学生深度诊断")
    
    student_list = df['姓名'].unique().tolist()
    selected_student = st.selectbox("请选择学生姓名：", student_list)
    
    if selected_student:
        student_data = df[df['姓名'] == selected_student].iloc[0]
        
        # 提取该学生有效成绩
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
            st.warning("该学生无有效成绩。")
        else:
            # --- 核心升级：计算总分 ---
            total_score = sum(my_scores)
            
            # 1. 展示大卡片 (KPI)
            st.markdown("### 📝 成绩单")
            col1, col2, col3 = st.columns(3)
            col1.metric("姓名", selected_student)
            col2.metric("考试科目数", f"{len(my_subjects)} 科")
            # 如果是全科满分750，这里可以自己换算，现在直接显示总分
            col3.metric("个人总分", f"{total_score:.1f} 分", delta_color="normal")

            # 2. 左右布局：左边雷达图，右边详细表格
            c1, c2 = st.columns([3, 2])
            
            with c1:
                # 闭合雷达图数据
                plot_subjects = my_subjects + [my_subjects[0]]
                plot_my_scores = my_scores + [my_scores[0]]
                plot_class_scores = class_scores + [class_scores[0]]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=plot_class_scores, theta=plot_subjects, fill='toself',
                    name='班级平均', line_color='gray', opacity=0.3
                ))
                fig.add_trace(go.Scatterpolar(
                    r=plot_my_scores, theta=plot_subjects, fill='toself',
                    name=selected_student, line_color='#1f77b4'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max(max(plot_my_scores), max(plot_class_scores)) + 10])),
                    margin=dict(t=30, b=30), # 调整边距让图更大
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("详细得分表")
                # 构造一个漂亮的表格
                score_dict = {sub: score for sub, score in zip(my_subjects, my_scores)}
                score_dict['【总分】'] = total_score # 把总分加进去
                
                # 转成表格展示
                display_df = pd.DataFrame(list(score_dict.items()), columns=['科目', '得分'])
                
                # 高亮显示总分行
                st.dataframe(
                    display_df, 
                    hide_index=True, 
                    use_container_width=True,
                    height=400 # 让表格和左边的图一样高
                )

except Exception as e:
    st.error(f"发生错误：{e}")