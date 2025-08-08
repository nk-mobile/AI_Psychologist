/ *static / admin / css / custom_admin.css * /

/ *Общие
улучшения
стиля * /
body
{
    background - color:  # f8f9fa !important;
}

# container {
display: flex;
flex - direction: column;
min - height: 100
vh;
}

# header {
background: linear - gradient(135
deg,  # 6a11cb 0%, #2575fc 100%) !important;
color: white !important;
border - bottom: none !important;
box - shadow: 0
2
px
4
px
rgba(0, 0, 0, 0.1);
padding: 10
px
20
px !important;
}

# branding h1, #branding h1 a:link, #branding h1 a:visited {
color: white !important;
font - size: 1.5
rem !important;
}

# user-tools {
color: rgba(255, 255, 255, 0.85) !important;
}

# user-tools a {
color: white !important;
text - decoration: underline;
}

.module
h2,.module
caption,.inline - group
h2
{
    background:  # e9ecef !important;
        color:  # 495057 !important;
font - size: 1.1
rem !important;
padding: 10
px
15
px !important;
}

.module
{
    border: 1px solid  # dee2e6 !important;
    border - radius: 8px !important;
box - shadow: 0
2
px
5
px
rgba(0, 0, 0, 0.05) !important;
margin - bottom: 20
px !important;
overflow: hidden !important;
}

/ *Стили
для
таблиц * /
table
{
    background - color: white !important;
border - collapse: separate !important;
border - spacing: 0 !important;
border - radius: 8
px !important;
overflow: hidden !important;
box - shadow: 0
1
px
3
px
rgba(0, 0, 0, 0.05) !important;
}

th
{
    background - color:  # f1f3f5 !important;
        color:  # 495057 !important;
font - weight: 600 !important;
padding: 12
px
15
px !important;
border - bottom: 1
px
solid  # dee2e6 !important;
}

td
{
    padding: 12px 15px !important;
border - bottom: 1
px
solid  # e9ecef !important;
}

tr: last - child
td
{
    border - bottom: none !important;
}

tr: hover
td
{
    background - color:  # f8f9fa !important;
}

/ * Стили
для
кнопок * /
.button, input[type = submit], input[type = button], .submit - row
input, a.button
{
    background: linear - gradient(135deg,  # 6a11cb 0%, #2575fc 100%) !important;
color: white !important;
border: none !important;
border - radius: 4
px !important;
padding: 8
px
16
px !important;
font - weight: 500 !important;
box - shadow: 0
2
px
4
px
rgba(0, 0, 0, 0.1) !important;
transition: all
0.2
s
ease - in -out !important;
}

.button: hover, input[type = submit]:hover, input[type = button]:hover,.submit - row
input: hover, a.button: hover
{
    opacity: 0.9 !important;
transform: translateY(-1
px) !important;
box - shadow: 0
4
px
8
px
rgba(0, 0, 0, 0.15) !important;
}

.button.default, input[type = submit].default,.submit - row
input.default
{
    background: linear - gradient(135deg,  # 28a745 0%, #20c997 100%) !important;
}

/ *Стили
для
форм * /
.form - row
{
    padding: 15px !important;
border - bottom: 1
px
solid  # e9ecef !important;
}

.form - row: last - child
{
    border - bottom: none !important;
}

/ *Стили
для
навигации * /
.breadcrumbs
{
    background - color:  # e9ecef !important;
        padding: 10
px
20
px !important;
border - bottom: 1
px
solid  # dee2e6 !important;
}

/ *Стили
для
боковой
панели * /
# content-related {
background - color:  # f8f9fa !important;
border - left: 1
px
solid  # dee2e6 !important;
border - radius: 0
8
px
8
px
0 !important;
}

/ *Адаптивность * /
   @ media(max - width: 768
px) {
    # container {
    padding: 10px !important;
}

.module
{
    margin - bottom: 15px !important;
}

th, td
{
    padding: 8px 10px !important;
}
}

/ *Стили
для
карточек
действий * /
# content-main .module {
background - color: white !important;
}

/ *Улучшенные
стили
для
ссылок * /
a: link, a: visited
{
    color:  # 0d6efd !important;
}

a: hover
{
    color:  # 0b5ed7 !important;
}

/ * Стили
для
сообщений * /
.messages
{
    margin: 20px 0 !important;
border - radius: 8
px !important;
overflow: hidden !important;
}

/ *Стили
для
поиска * /
# changelist-search {
background - color: white !important;
padding: 20
px !important;
border - radius: 8
px !important;
box - shadow: 0
2
px
5
px
rgba(0, 0, 0, 0.05) !important;
margin - bottom: 20
px !important;
}

/ *Стили
для
фильтров * /
# changelist-filter {
background - color: white !important;
border - radius: 8
px !important;
box - shadow: 0
2
px
5
px
rgba(0, 0, 0, 0.05) !important;
padding: 20
px !important;
margin - bottom: 20
px !important;
}

/ *Стили
для
футера * /
# footer {
background - color:  # f8f9fa !important;
border - top: 1
px
solid  # dee2e6 !important;
padding: 20
px !important;
margin - top: auto !important;
}