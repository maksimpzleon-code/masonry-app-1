import streamlit as st
import pandas as pd
from geometry.shape import build_shape, reduce_shape
from geometry.nodes import Node
from plotting.images import build_image_1, build_image_2


# ------------------ Инициализация состояния ------------------
def init_session_state():
    if "geom_ok" not in st.session_state:
        st.session_state.geom_ok = True
    if "force_ok" not in st.session_state:
        st.session_state.force_ok = True
    if "geom_params" not in st.session_state:
        st.session_state.geom_params = {
            "a1": 1810, "b1": 510,
            "a2": 640, "b2": 250, "c2": 120,
            "a3": 770, "b3": 380, "c3": 900
        }
    if "main_shape" not in st.session_state:
        st.session_state.main_shape = build_shape(st.session_state.geom_params)
    if "force_params" not in st.session_state:
        st.session_state.force_params = {
            "force": 46.2,
            "moment_x": 2.7,
            "moment_y": 3.1
        }
    if "force_node" not in st.session_state:
        st.session_state.force_node = Node(
            st.session_state.main_shape.center.x + 1000 * st.session_state.force_params["moment_y"] /
            st.session_state.force_params["force"],
            st.session_state.main_shape.center.y + 1000 * st.session_state.force_params["moment_x"] /
            st.session_state.force_params["force"]
        )
    if "red_shape" not in st.session_state:
        st.session_state.red_shape = reduce_shape(st.session_state.geom_params, st.session_state.force_node)


# ------------------ Интерфейс: размеры сечения ------------------
def section_dimensions():
    st.subheader("Размеры сечения")
    col_form, col_plot = st.columns([1, 2])
    submit_geom = False

    with col_form:
        with st.form("param_form1"):
            st.write("Стена, мм")
            f1, f2 = st.columns(2)
            with f1:
                a1 = st.number_input("$a_1$", min_value=120, key="a1", value=st.session_state.geom_params["a1"])
            with f2:
                b1 = st.number_input("$b_1$", min_value=120, key="b1", value=st.session_state.geom_params["b1"])

            st.write("Верхний пилон, мм")
            f1, f2, f3 = st.columns(3)
            with f1:
                a2 = st.number_input("$a_2$", min_value=0, key="a2", value=st.session_state.geom_params["a2"])
            with f2:
                b2 = st.number_input("$b_2$", min_value=0, key="b2", value=st.session_state.geom_params["b2"])
            with f3:
                c2 = st.number_input("$c_2$", min_value=0, key="c2", value=st.session_state.geom_params["c2"],
                                     help="Если пилон отсутствует, задайте нулевые значения")

            st.write("Нижний пилон, мм")
            f1, f2, f3 = st.columns(3)
            with f1:
                a3 = st.number_input("$a_3$", min_value=0, key="a3", value=st.session_state.geom_params["a3"])
            with f2:
                b3 = st.number_input("$b_3$", min_value=0, key="b3", value=st.session_state.geom_params["b3"])
            with f3:
                c3 = st.number_input("$c_3$", min_value=0, key="c3", value=st.session_state.geom_params["c3"],
                                     help="Если пилон отсутствует, задайте нулевые значения")

            submit_geom = st.form_submit_button("Применить")

    if submit_geom:
        if c2 + a2 > a1:
            st.error("Требуется, чтобы $$c_2 + a_2 ≤ a_1$$")
            st.session_state.geom_ok = False
        elif c3 + a3 > a1:
            st.error("Требуется, чтобы $$c_3 + a_3 ≤ a_1$$")
            st.session_state.geom_ok = False
        else:
            st.session_state.geom_params = {
                "a1": st.session_state.a1, "b1": st.session_state.b1,
                "a2": st.session_state.a2, "b2": st.session_state.b2, "c2": st.session_state.c2,
                "a3": st.session_state.a3, "b3": st.session_state.b3, "c3": st.session_state.c3
            }
            st.session_state.main_shape = build_shape(st.session_state.geom_params)
            st.session_state.geom_ok = True
            st.session_state.force_ok = False

    with col_plot:
        col1, col2 = st.columns([1, 3])
        with col1:
            toggle_dimensions = st.toggle("Размеры", value=True)
        with col2:
            toggle_notation = st.toggle("Обозначения", value=True)

        fig = build_image_1(toggle_dimensions, toggle_notation,
                            st.session_state.geom_params,
                            st.session_state.main_shape.nodes,
                            st.session_state.main_shape.center)
        st.pyplot(fig)


# ------------------ Интерфейс: внутренние усилия ------------------
def internal_forces():
    st.subheader("Расчет геометрии сжатой зоны сечения")
    col_form, col_plot = st.columns([1, 2])
    submit_force = False

    with col_form:
        with st.form("param_form2"):
            st.write("Внутренние усилия")
            force = st.number_input("Сила $N$, кН", key="force", step=0.1, min_value=1.0,
                                    value=st.session_state.force_params["force"])
            moment_x = st.number_input("Момент $M_x$, кНм", key="moment_x", step=0.1,
                                       value=st.session_state.force_params["moment_x"])
            moment_y = st.number_input("Момент $M_y$, кНм", key="moment_y", step=0.1,
                                       value=st.session_state.force_params["moment_y"])
            submit_force = st.form_submit_button("Рассчитать")

    if submit_force:
        try:
            st.session_state.force_params = {
                "force": st.session_state.force,
                "moment_x": st.session_state.moment_x,
                "moment_y": st.session_state.moment_y
            }

            st.session_state.force_node = Node(
                st.session_state.main_shape.center.x + 1000 * st.session_state.force_params["moment_y"] /
                st.session_state.force_params["force"],
                st.session_state.main_shape.center.y + 1000 * st.session_state.force_params["moment_x"] /
                st.session_state.force_params["force"]
            )

            st.session_state.red_shape = reduce_shape(st.session_state.geom_params, st.session_state.force_node)
            st.session_state.force_ok = True
        except ValueError as e:
            st.session_state.force_ok = False
            st.error(str(e))

    with col_plot:
        if st.session_state.geom_ok and st.session_state.force_ok:
            fig = build_image_2(st.session_state.main_shape.nodes,
                                st.session_state.red_shape.nodes,
                                st.session_state.main_shape.center,
                                st.session_state.red_shape.center,
                                st.session_state.force_node)
            st.pyplot(fig)
        else:
            st.warning("Проведите расчет сжатой зоны", icon="⚠️")


# ------------------ Таблица геометрических характеристик ------------------
def geometric_characteristics():
    if st.session_state.geom_ok and st.session_state.force_ok:
        with st.expander("Геометрические характеристики"):
            sq_main = st.session_state.main_shape.square / 10 ** 2
            ix_main = st.session_state.main_shape.inertia_moment[0] / 10 ** 4
            iy_main = st.session_state.main_shape.inertia_moment[1] / 10 ** 4
            rx_main = st.session_state.main_shape.inertia_radius[0] / 10
            ry_main = st.session_state.main_shape.inertia_radius[1] / 10
            ex_main = (st.session_state.force_node.x - st.session_state.main_shape.center.x) / 10
            ey_main = (st.session_state.force_node.y - st.session_state.main_shape.center.y) / 10
            sq_red = st.session_state.red_shape.square / 10 ** 2
            ix_red = st.session_state.red_shape.inertia_moment[0] / 10 ** 4
            iy_red = st.session_state.red_shape.inertia_moment[1] / 10 ** 4
            rx_red = st.session_state.red_shape.inertia_radius[0] / 10
            ry_red = st.session_state.red_shape.inertia_radius[1] / 10
            ex_red = (st.session_state.force_node.x - st.session_state.red_shape.center.x) / 10
            ey_red = (st.session_state.force_node.y - st.session_state.red_shape.center.y) / 10

            df = pd.DataFrame(
                [
                    ["$A$", "$I_x$", "$I_y$", "$i_x$", "$i_y$", "$e_x$", "$e_y$"],
                    ["$см^2$", "$см^4$", "$см^4$", "$см$", "$см$", "$см$", "$см$"],
                    [sq_main, ix_main, iy_main, rx_main, ry_main, ex_main, ey_main],
                    [sq_red, ix_red, iy_red, rx_red, ry_red, ex_red, ey_red],
                ],
                index=["Обозн.", "Ед. изм.", "Полное сечение", "Сжатая зона"],
                columns=["Площадь", "Момент инерции по оси x", "Момент инерции по оси y",
                         "Радиус инерции по оси x", "Радиус инерции по оси y",
                         "Эксцентриситет по оси x", "Эксцентриситет по оси y"]
            )

            for row in ["Полное сечение", "Сжатая зона"]:
                df.loc[row] = df.loc[row].map(
                    lambda x: f"{x:.2f}".replace(".", ",") if isinstance(x, (int, float)) else x)

            st.table(df.T, border="horizontal")


# ------------------ Основная функция ------------------
def main():
    st.markdown(
        """
        <style>
        /* Подключение Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

        /* Формулы KaTeX */
        .katex { font-size: 1.1em !important; }        

        /* Заголовки — Inter */
        h1, h2, h3, h4, h5, h6, .stTitle, .stHeader, .stSubheader {
            font-family: 'Inter', sans-serif !important;
        }

        /* Размеры заголовков */
        h1, .stTitle { font-size: 2.25em !important; }
        h2, .stHeader { font-size: 1.75em !important; }
        h3, .stSubheader { font-size: 1.5em !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.link_button("Вернуться к списку приложений", url="https://google.com", icon="🏃")
    st.title("Косое внецентренное сжатие каменных сечений")

    init_session_state()

    section_dimensions()
    st.divider()
    internal_forces()
    geometric_characteristics()
    st.divider()
    st.subheader("Расчет прочности в разработке")

if __name__ == "__main__":
    main()

