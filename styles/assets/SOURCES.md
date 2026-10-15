# 风格库素材来源

## 照片（全部来自 Pexels，Pexels License：免费商用、无需署名，可修改；不得原样转售或暗示人物/品牌背书）
本地文件均在 `styles/assets/raw/`，下载地址格式 `https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=2400`。
调色/裁切/网点化后的版本由代码生成到 `styles/assets/gen/`（可删除后重新生成）。作者"未取到"= Pexels 页面被 Cloudflare 拦截，未能读取作者名，来源页链接仍有效。

| 本地文件 | Pexels ID / 来源页 | 作者 | 用在哪 |
|---|---|---|---|
| scrap_picnic.jpg | [8380028](https://www.pexels.com/photo/8380028/) 海边野餐 | Kampus Production | 手账 p1 |
| scrap_coffee.jpg | [2305760](https://www.pexels.com/photo/2305760/) 咖啡、相机与地图 | 未取到 | 手账 p1 |
| scrap_photos.jpg | [10064628](https://www.pexels.com/photo/10064628/) 旧照片、书与胶片相机 | hello aesthe | 手账 p2 |
| scrap_friends.jpg | [33867307](https://www.pexels.com/photo/33867307/) 公园里的朋友 | Loverice Lah | 手账 p3、p7 |
| scrap_blanket.jpg | [8531237](https://www.pexels.com/photo/8531237/) 野餐毯上的女孩们 | KoolShooters | 手账 p3 |
| scrap_street.jpg | [24014253](https://www.pexels.com/photo/24014253/) 海边小镇街道 | Ricardo Moreira | 手账 p3 |
| scrap_town.jpg | [16002695](https://www.pexels.com/photo/16002695/) 芒通海岸 | SlimMars 13 | 手账 p4、p5 |
| edit_window.jpg | [12567395](https://www.pexels.com/photo/12567395/) 窗台咖啡与书 | Ioana Motoc | 杂志 p1 |
| edit_sun.jpg | [30349296](https://www.pexels.com/photo/30349296/) 阳光下的咖啡与书 | 未取到 | 杂志 p3 |
| edit_reader.jpg | [6965743](https://www.pexels.com/photo/6965743/) 窗边读书 | cottonbro studio | 杂志 p4 |
| edit_table.jpg | [37438637](https://www.pexels.com/photo/37438637/) 木桌上的咖啡与书 | Nur Nur | 杂志 p8 |
| aur_head2.jpg | [18254089](https://www.pexels.com/photo/18254089/) 挂在墙上的耳机（无品牌标识） | 未取到 | 极光 p3 |
| aur_head.jpg | [9154411](https://www.pexels.com/photo/9154411/) 黑色耳机特写（只裁头梁部分，避开品牌标识） | Adrian Regeci | 极光 p5 |
| glass_team.jpg | [36765681](https://www.pexels.com/photo/36765681/) 明亮办公室协作 | Vitaly Gariev | 玻璃 p4 |
| glass_sky2.jpg | [35690368](https://www.pexels.com/photo/35690368/) 粉彩晚霞云 | 未取到 | 玻璃 p6 |
| riso_harvest.jpg | [7658779](https://www.pexels.com/photo/7658779/) 菜园收获 | Kampus Production | 孔版 p1 |
| riso_roof.jpg | [9722008](https://www.pexels.com/photo/9722008/) 一起种植物 | cottonbro studio | 孔版 p2 |
| riso_tomato.jpg | [37408649](https://www.pexels.com/photo/37408649/) 市集番茄 | 未取到 | 孔版 p5 |
| riso_crates.jpg | [15279910](https://www.pexels.com/photo/15279910/) 木箱里的蔬菜 | 未取到 | 孔版 p7 |
| jp_cups.jpg | [4830753](https://www.pexels.com/photo/4830753/) 手作陶杯 | Diana Light | 日式 p1 |
| jp_making.jpg | [8748549](https://www.pexels.com/photo/8748549/) 泡茶 | cottonbro studio | 日式 p2 |
| jp_bamboo.jpg | [30980932](https://www.pexels.com/photo/30980932/) 京都竹林 | 未取到 | 日式 p6 |
| gs_terrace.jpg | [35534147](https://www.pexels.com/photo/35534147/) 巴厘岛梯田航拍 | Tom Fisk | 国赛 p1 |
| gs_planting.jpg | [3232602](https://www.pexels.com/photo/3232602/) 插秧 | Quang Nguyen Vinh | 国赛 p2 |
| gs_field.jpg | [6726929](https://www.pexels.com/photo/6726929/) 农田航拍 | 未取到 | 国赛 p3 |
| gs_drone.jpg | [34182315](https://www.pexels.com/photo/34182315/) 田间无人机 | 未取到 | 国赛 p4 |
| gs_seedling.jpg | [12969371](https://www.pexels.com/photo/12969371/) 手捧幼苗 | 未取到 | 国赛 p6 |
| gs_green.jpg | [30619295](https://www.pexels.com/photo/30619295/) 温室幼苗 | 未取到 | 国赛 p6 |
| gs_terrace2.jpg | [2036412](https://www.pexels.com/photo/2036412/) 梯田航拍 | Tom Fisk | 国赛 p6、p7 |

另下载未使用（备用）：glass_sky、glass_bokeh、glass_office、gs_drone2、riso_plant（与 gs_planting 同图）、jp_still、jp_matcha（Pexels 31199969）、edit 系列以外的若干。

## 程序生成素材（无 AI 生成图）
全部由 `lib/styles/textures.py` 用 numpy/Pillow 生成：皱纸、纸胶带、横格纸、牛皮纸、颗粒层、极光/柔彩光斑、模糊背景、渐变球体、径向光晕、暗角、镜头光条、双色网点照片、网点色块、和纸、印章（字形来自开源 Noto Serif CJK）、干笔刷痕。
