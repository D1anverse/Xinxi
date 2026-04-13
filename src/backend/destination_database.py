"""
约会地点数据库
为 SoulMatch AI 助手提供丰富的目的地推荐
"""

DESTINATION_DATABASE = {
    # ============================================
    # 一线城市
    # ============================================
    "深圳": {
        "室内约会": [
            {"name": "方所书店", "type": "文艺书店", "address": "深圳万象城B1层", "price": "免费", "tips": "环境优雅，适合安静的聊天"},
            {"name": "深圳博物馆", "type": "博物馆", "address": "市民中心", "price": "免费(需预约)", "tips": "了解深圳历史，常有特展"},
            {"name": "深圳图书馆", "type": "图书馆", "address": "福田区中心书城", "price": "免费", "tips": "自习区氛围好，有咖啡厅"},
            {"name": "欢乐谷", "type": "游乐园", "address": "南山区侨城西街", "price": "¥220/人", "tips": "大型游乐场，玩一整天"},
            {"name": "深圳当代艺术馆", "type": "艺术馆", "address": "市民中心", "price": "免费", "tips": "建筑超美，拍照圣地"},
            {"name": "华强北博物馆", "type": "博物馆", "address": "华强北街道", "price": "免费", "tips": "了解电子科技发展史"},
            {"name": "iFLY跳伞俱乐部", "type": "运动体验", "address": "宝安区", "price": "¥600+/人", "tips": "室内风洞飞行，超刺激"},
            {"name": "射击俱乐部", "type": "运动体验", "address": "各区都有", "price": "¥200-500", "tips": "真人CS或射击，超解压"},
            {"name": "保龄球馆", "type": "运动娱乐", "address": "各区都有", "price": "¥80-150/人", "tips": "互动性强，容易上手"},
            {"name": "密室逃脱", "type": "解谜游戏", "address": "各区都有", "price": "¥88-158/人", "tips": "需要合作，快速破冰"},
        ],
        "户外约会": [
            {"name": "深圳湾公园", "type": "海滨公园", "address": "南山区滨海大道", "price": "免费", "tips": "海边骑行，看海景日落"},
            {"name": "大梅沙海滨公园", "type": "海滩", "address": "盐田区大梅沙", "price": "免费", "tips": "深圳最知名海滩，夏天必去"},
            {"name": "小梅沙", "type": "海滩", "address": "盐田区", "price": "¥50", "tips": "比大梅沙人少，水更清"},
            {"name": "人才公园", "type": "城市公园", "address": "南山区后海", "price": "免费", "tips": "夜景超美，晚上约会首选"},
            {"name": "梧桐岛", "type": "生态园区", "address": "宝安区固戍", "price": "免费", "tips": "小众秘境，拍照很出片"},
            {"name": "大鹏所城", "type": "古城", "address": "大鹏新区", "price": "免费", "tips": "600年古城，小吃很多"},
            {"name": "较场尾海滩", "type": "海滩", "address": "大鹏新区", "price": "免费", "tips": "民宿小镇，文艺小清新"},
            {"name": "杨梅坑", "type": "海边", "address": "大鹏新区", "price": "免费", "tips": "《美人鱼》取景地，风景绝美"},
            {"name": "仙湖植物园", "type": "植物园", "address": "罗湖区", "price": "¥15", "tips": "弘法寺祈福，植物很多"},
            {"name": "莲花山公园", "type": "城市公园", "address": "福田区", "price": "免费", "tips": "俯瞰市民中心，俯瞰全城夜景"},
            {"name": "笔架山公园", "type": "城市公园", "address": "福田区", "price": "免费", "tips": "野餐的好地方"},
            {"name": "塘朗山公园", "type": "登山", "address": "南山区", "price": "免费", "tips": "登顶看深圳全景"},
        ],
        "美食约会": [
            {"name": "东门町美食街", "type": "美食街", "address": "罗湖区东门", "price": "¥50-100/人", "tips": "小吃一条街，选择超多"},
            {"name": "海岸城", "type": "购物中心", "address": "南山区文心五路", "price": "¥100-300/人", "tips": "餐厅选择多，环境好"},
            {"name": "欢乐港湾", "type": "滨海商业", "address": "宝安区", "price": "¥100-200/人", "tips": "摩天轮夜景超浪漫"},
            {"name": "水围1368文化街", "type": "美食街", "address": "福田区水围村", "price": "¥60-120/人", "tips": "城中村美食，本地人常去"},
            {"name": "车公庙食街", "type": "美食街", "address": "福田区车公庙", "price": "¥50-150/人", "tips": "各式菜系应有尽有"},
            {"name": "香蜜湖美食城", "type": "美食城", "address": "福田区香蜜湖", "price": "¥80-200/人", "tips": "老字号多，口碑好"},
            {"name": "深业上城", "type": "购物中心", "address": "福田区", "price": "¥100-250/人", "tips": "小镇风格，拍照好看"},
        ],
        "文艺约会": [
            {"name": "华侨城创意园", "type": "文创园", "address": "南山区华侨城", "price": "免费", "tips": "文创小店，文艺青年必去"},
            {"name": "大芬油画村", "type": "艺术村", "address": "龙岗区布吉", "price": "免费", "tips": "可以买画或体验画油画"},
            {"name": "南海意库", "type": "文创园", "address": "南山区", "price": "免费", "tips": "小众文创园，人少安静"},
            {"name": "高北十六创意园", "type": "文创园", "address": "南山区", "price": "免费", "tips": "经常有创意市集"},
            {"name": "深圳大学", "type": "校园", "address": "南山区", "price": "免费", "tips": "深大网红楼，拍照超好看"},
        ],
        "夜生活": [
            {"name": "海上世界", "type": "休闲区", "address": "南山区蛇口", "price": "¥100-300", "tips": "明华轮夜景，音乐喷泉"},
            {"name": "华强北九方", "type": "酒吧街", "address": "福田区华强北", "price": "¥100-200", "tips": "清吧比较多，环境安静"},
            {"name": "欢乐海岸", "type": "休闲区", "address": "南山区", "price": "¥100-300", "tips": "水秀剧场，夜景很美"},
        ]
    },

    "广州": {
        "室内约会": [
            {"name": "广东省博物馆", "type": "博物馆", "address": "珠江新城", "price": "免费(需预约)", "tips": "建筑超有设计感"},
            {"name": "正佳广场极地海洋世界", "type": "海洋馆", "address": "天河区", "price": "¥198/人", "tips": "室内海洋馆，超浪漫"},
            {"name": "方所书店", "type": "文艺书店", "address": "天河区太古汇", "price": "免费", "tips": "广州最文艺的书店"},
            {"name": "广州图书馆", "type": "图书馆", "address": "珠江新城", "price": "免费", "tips": "建筑设计很酷"},
            {"name": "华南植物园", "type": "植物园", "address": "天河区", "price": "¥20", "tips": "温室植物王国"},
        ],
        "户外约会": [
            {"name": "沙面岛", "type": "历史街区", "address": "荔湾区", "price": "免费", "tips": "欧式建筑，拍照圣地"},
            {"name": "海珠湿地公园", "type": "湿地公园", "address": "海珠区", "price": "¥20", "tips": "城市绿肺，空气清新"},
            {"name": "白云山", "type": "山脉", "address": "白云区", "price": "¥5", "tips": "广州最高峰，爬山锻炼"},
            {"name": "二沙岛", "type": "江心岛", "address": "越秀区", "price": "免费", "tips": "野餐首选，CBD夜景"},
            {"name": "大夫山森林公园", "type": "森林公园", "address": "番禺区", "price": "免费", "tips": "骑行、烧烤的好地方"},
            {"name": "海珠湖公园", "type": "湖泊公园", "address": "海珠区", "price": "免费", "tips": "花海超美，适合拍照"},
        ],
        "美食约会": [
            {"name": "北京路步行街", "type": "美食街", "address": "越秀区", "price": "¥50-150/人", "tips": "老字号美食云集"},
            {"name": "上下九步行街", "type": "美食街", "address": "荔湾区", "price": "¥50-100/人", "tips": "广州特色小吃一条街"},
            {"name": "太古汇", "type": "购物中心", "address": "天河区", "price": "¥150-400/人", "tips": "高端餐厅聚集地"},
            {"name": "天环广场", "type": "购物中心", "address": "天河区", "price": "¥100-300/人", "tips": "轻奢品牌多，建筑好看"},
            {"name": "番禺长隆", "type": "综合娱乐", "address": "番禺区", "price": "¥200-500", "tips": "动物园/欢乐世界/水上乐园"},
        ],
        "文艺约会": [
            {"name": "红砖厂创意园", "type": "文创园", "address": "天河区", "price": "免费", "tips": "广州网红文创园"},
            {"name": "289艺术园区", "type": "文创园", "address": "越秀区", "price": "免费", "tips": "常有艺术展览"},
            {"name": "中山大学", "type": "校园", "address": "海珠区", "price": "免费", "tips": "百年名校，校园很美"},
        ]
    },

    "北京": {
        "室内约会": [
            {"name": "中国国家博物馆", "type": "博物馆", "address": "天安门广场东侧", "price": "免费(需预约)", "tips": "顶级博物馆，超级震撼"},
            {"name": "故宫博物院", "type": "博物馆", "address": "东城区景山前街", "price": "¥60", "tips": "必去！提前预约"},
            {"name": "798艺术区", "type": "艺术区", "address": "朝阳区酒仙桥", "price": "免费", "tips": "文创画廊云集"},
            {"name": "中国美术馆", "type": "美术馆", "address": "东城区五四大街", "price": "免费(需预约)", "tips": "经常有大师展"},
            {"name": "国家图书馆", "type": "图书馆", "address": "海淀区中关村", "price": "免费", "tips": "亚洲最大图书馆"},
        ],
        "户外约会": [
            {"name": "颐和园", "type": "皇家园林", "address": "海淀区", "price": "¥60", "tips": "超大型园林，逛一天"},
            {"name": "北海公园", "type": "城市公园", "address": "西城区", "price": "¥10", "tips": "划船超浪漫"},
            {"name": "什刹海", "type": "历史街区", "address": "西城区", "price": "免费", "tips": "胡同游，后海酒吧街"},
            {"name": "故宫角楼", "type": "景点", "address": "东城区", "price": "免费", "tips": "拍照超美，日落绝景"},
            {"name": "香山公园", "type": "山景公园", "address": "海淀区", "price": "¥15", "tips": "秋天红叶超美"},
            {"name": "奥林匹克公园", "type": "城市公园", "address": "朝阳区", "price": "免费", "tips": "鸟巢水立方夜景"},
        ],
        "美食约会": [
            {"name": "簋街", "type": "美食街", "address": "东城区", "price": "¥80-200/人", "tips": "24小时营业，小龙虾一条街"},
            {"name": "南锣鼓巷", "type": "美食街", "address": "东城区", "price": "¥50-150/人", "tips": "网红小吃云集"},
            {"name": "王府井", "type": "商业街", "address": "东城区", "price": "¥100-300/人", "tips": "老牌商业街"},
            {"name": "三里屯", "type": "时尚区", "address": "朝阳区", "price": "¥150-500/人", "tips": "酒吧餐厅云集"},
        ]
    },

    "上海": {
        "室内约会": [
            {"name": "上海博物馆", "type": "博物馆", "address": "黄浦区人民广场", "price": "免费(需预约)", "tips": "青铜器馆超震撼"},
            {"name": "上海当代艺术博物馆", "type": "艺术馆", "address": "黄浦区", "price": "免费", "tips": "工业风建筑，很出片"},
            {"name": "外滩星空错觉艺术馆", "type": "体验馆", "address": "黄浦区", "price": "¥68/人", "tips": "网红拍照地"},
            {"name": "上海油罐艺术中心", "type": "艺术馆", "address": "徐汇区", "price": "免费", "tips": "超现代建筑"},
        ],
        "户外约会": [
            {"name": "外滩", "type": "景观", "address": "黄浦区", "price": "免费", "tips": "必去！夜景超美"},
            {"name": "豫园", "type": "古典园林", "address": "黄浦区", "price": "¥40", "tips": "城隍庙小吃+豫园"},
            {"name": "田子坊", "type": "石库门", "address": "黄浦区", "price": "免费", "tips": "弄堂小店，文艺清新"},
            {"name": "1933老场坊", "type": "创意园", "address": "虹口区", "price": "免费", "tips": "《小时代》取景地"},
            {"name": "泰晤士小镇", "type": "英伦小镇", "address": "松江区", "price": "免费", "tips": "假装在国外，适合拍照"},
        ],
        "美食约会": [
            {"name": "南京路步行街", "type": "商业街", "address": "黄浦区", "price": "¥100-300/人", "tips": "上海最知名商业街"},
            {"name": "新天地", "type": "时尚区", "address": "黄浦区", "price": "¥150-500/人", "tips": "石库门改造的时尚地标"},
            {"name": "城隍庙", "type": "美食区", "address": "黄浦区", "price": "¥50-150/人", "tips": "上海特色小吃"},
            {"name": "思南路", "type": "法租界", "address": "黄浦区", "price": "¥100-300/人", "tips": "浪漫法式风情"},
        ]
    },

    # ============================================
    # 新一线城市
    # ============================================
    "成都": {
        "室内约会": [
            {"name": "成都博物馆", "type": "博物馆", "address": "青羊区", "price": "免费(需预约)", "tips": "了解成都历史"},
            {"name": "方所书店", "type": "文艺书店", "address": "锦江区太古里", "price": "免费", "tips": "地下书店，超有格调"},
            {"name": "东郊记忆", "type": "文创园", "address": "成华区", "price": "免费", "tips": "工业风文创园"},
        ],
        "户外约会": [
            {"name": "宽窄巷子", "type": "历史街区", "address": "青羊区", "price": "免费", "tips": "成都必去！喝茶采耳"},
            {"name": "锦里古街", "type": "历史街区", "address": "武侯祠大街", "price": "免费", "tips": "夜景超美，小吃很多"},
            {"name": "人民公园", "type": "城市公园", "address": "青羊区", "price": "免费", "tips": "鹤鸣茶社，掏耳朵"},
            {"name": "望平街", "type": "滨河街", "address": "成华区", "price": "免费", "tips": "新晋网红街，咖啡店林立"},
        ],
        "美食约会": [
            {"name": "玉林路", "type": "美食街", "address": "武侯区", "price": "¥50-100/人", "tips": "《成都》歌里的地方"},
            {"name": "建设路小吃街", "type": "小吃街", "address": "成华区", "price": "¥30-80/人", "tips": "学生党美食天堂"},
            {"name": "太古里", "type": "购物中心", "address": "锦江区", "price": "¥100-400/人", "tips": "高端时尚地标"},
        ]
    },

    "杭州": {
        "室内约会": [
            {"name": "中国丝绸博物馆", "type": "博物馆", "address": "西湖区", "price": "免费", "tips": "丝绸文化，超大展厅"},
            {"name": "浙江图书馆", "type": "图书馆", "address": "西湖区", "price": "免费", "tips": "环境很好"},
        ],
        "户外约会": [
            {"name": "西湖", "type": "湖泊", "address": "西湖区", "price": "免费", "tips": "环湖骑行，断桥残雪"},
            {"name": "太子湾公园", "type": "公园", "address": "西湖区", "price": "免费", "tips": "春天花海超美"},
            {"name": "灵隐寺", "type": "寺庙", "address": "西湖区", "price": "¥75(含灵隐)", "tips": "杭州最知名寺庙"},
            {"name": "宋城", "type": "主题公园", "address": "西湖区", "price": "¥300+", "tips": "《宋城千古情》超震撼"},
        ],
        "美食约会": [
            {"name": "河坊街", "type": "美食街", "address": "上城区", "price": "¥50-150/人", "tips": "杭州老街，小吃云集"},
            {"name": "南山路", "type": "风情街", "address": "上城区", "price": "¥100-300/人", "tips": "酒吧咖啡一条街"},
        ]
    },

    "武汉": {
        "室内约会": [
            {"name": "湖北省博物馆", "type": "博物馆", "address": "武昌区", "price": "免费", "tips": "曾侯乙编钟，越王勾践剑"},
            {"name": "武汉美术馆", "type": "美术馆", "address": "江岸区", "price": "免费", "tips": "常有大师展"},
        ],
        "户外约会": [
            {"name": "东湖绿道", "type": "绿道", "address": "武昌区", "price": "免费", "tips": "骑行超棒，空气清新"},
            {"name": "武汉大学", "type": "校园", "address": "武昌区", "price": "免费", "tips": "樱花季超美"},
            {"name": "昙华林", "type": "历史街区", "address": "武昌区", "price": "免费", "tips": "文艺小清新"},
            {"name": "楚河汉街", "type": "商业街", "address": "武昌区", "price": "¥100-300", "tips": "欧式建筑，超长步行街"},
        ],
        "美食约会": [
            {"name": "户部巷", "type": "小吃街", "address": "武昌区", "price": "¥30-80/人", "tips": "武汉小吃一条街"},
            {"name": "吉庆街", "type": "美食街", "address": "江岸区", "price": "¥50-150/人", "tips": "老字号美食云集"},
        ]
    },

    "南京": {
        "室内约会": [
            {"name": "南京博物院", "type": "博物馆", "address": "玄武区", "price": "免费(需预约)", "tips": "中国三大博物馆之一"},
            {"name": "先锋书店", "type": "文艺书店", "address": "鼓楼区", "price": "免费", "tips": "地下车库改造，超文艺"},
        ],
        "户外约会": [
            {"name": "中山陵", "type": "陵墓景区", "address": "玄武区", "price": "免费", "tips": "南京必去！台阶超多"},
            {"name": "玄武湖", "type": "湖泊公园", "address": "玄武区", "price": "免费", "tips": "环湖散步超浪漫"},
            {"name": "老门东", "type": "历史街区", "address": "秦淮区", "price": "免费", "tips": "城墙下的小吃街"},
            {"name": "夫子庙", "type": "历史街区", "address": "秦淮区", "price": "免费", "tips": "秦淮夜景超美"},
        ],
        "美食约会": [
            {"name": "狮子桥美食街", "type": "美食街", "address": "鼓楼区", "price": "¥50-150/人", "tips": "老字号云集"},
            {"name": "新街口", "type": "商业区", "address": "玄武区", "price": "¥100-300/人", "tips": "大型商场云集"},
        ]
    },

    "西安": {
        "室内约会": [
            {"name": "陕西历史博物馆", "type": "博物馆", "address": "雁塔区", "price": "免费(需预约)", "tips": "中国顶级博物馆"},
            {"name": "大唐不夜城", "type": "商业街", "address": "雁塔区", "price": "免费", "tips": "不倒翁小姐姐，超浪漫"},
        ],
        "户外约会": [
            {"name": "城墙", "type": "城墙", "address": "市中心", "price": "¥54", "tips": "骑自行车环城超浪漫"},
            {"name": "大雁塔", "type": "古塔", "address": "雁塔区", "price": "¥40", "tips": "亚洲最大音乐喷泉"},
            {"name": "钟楼", "type": "古建筑", "address": "市中心", "price": "¥30", "tips": "西安地标，夜景超美"},
            {"name": "回民街", "type": "美食街", "address": "莲湖区", "price": "¥50-150/人", "tips": "清真美食云集"},
        ],
        "美食约会": [
            {"name": "永兴坊", "type": "美食街", "address": "新城区", "price": "¥50-150/人", "tips": "网红摔碗酒发源地"},
            {"name": "小寨", "type": "商业区", "address": "雁塔区", "price": "¥100-300/人", "tips": "年轻人聚集地"},
        ]
    },

    "重庆": {
        "室内约会": [
            {"name": "重庆中国三峡博物馆", "type": "博物馆", "address": "渝中区", "price": "免费", "tips": "了解三峡文化"},
            {"name": "钟书阁", "type": "文艺书店", "address": "九龙坡区", "price": "免费", "tips": "魔幻书店，超出片"},
        ],
        "户外约会": [
            {"name": "洪崖洞", "type": "景点", "address": "渝中区", "price": "免费", "tips": "千与千寻同款，夜景绝美"},
            {"name": "解放碑", "type": "地标", "address": "渝中区", "price": "免费", "tips": "重庆地标，购物美食"},
            {"name": "长江索道", "type": "交通", "address": "渝中区", "price": "¥20-30", "tips": "飞越长江，俯瞰夜景"},
            {"name": "鹅岭二厂", "type": "文创园", "address": "渝中区", "price": "免费", "tips": "老厂改造，文艺打卡地"},
            {"name": "南山一棵树", "type": "观景台", "address": "南岸区", "price": "¥30", "tips": "看重庆夜景最佳位置"},
        ],
        "美食约会": [
            {"name": "磁器口古镇", "type": "美食街", "address": "沙坪坝区", "price": "免费", "tips": "重庆小吃一条街"},
            {"name": "观音桥步行街", "type": "商业街", "address": "江北区", "price": "¥100-300", "tips": "重庆时尚地标"},
        ]
    },

    "苏州": {
        "户外约会": [
            {"name": "平江路", "type": "历史街区", "address": "姑苏区", "price": "免费", "tips": "苏州最美古街，小桥流水"},
            {"name": "拙政园", "type": "园林", "address": "姑苏区", "price": "¥70", "tips": "中国四大园林之一"},
            {"name": "苏州大学", "type": "校园", "address": "姑苏区", "price": "免费", "tips": "民国风校园，超美"},
            {"name": "金鸡湖", "type": "湖泊", "address": "工业园区", "price": "免费", "tips": "现代苏州，夜景超美"},
        ],
        "美食约会": [
            {"name": "观前街", "type": "美食街", "address": "姑苏区", "price": "¥50-150/人", "tips": "苏州老字号云集"},
            {"name": "山塘街", "type": "美食街", "address": "姑苏区", "price": "免费", "tips": "千年古街，夜景超美"},
        ]
    },

    "长沙": {
        "室内约会": [
            {"name": "湖南省博物馆", "type": "博物馆", "address": "开福区", "price": "免费(需预约)", "tips": "马王堆汉墓，超震撼"},
            {"name": "谢子龙影像艺术馆", "type": "艺术馆", "address": "岳麓区", "price": "¥80", "tips": "网红艺术馆，超出片"},
        ],
        "户外约会": [
            {"name": "橘子洲", "type": "公园", "address": "岳麓区", "price": "免费", "tips": "毛主席雕像，骑行超棒"},
            {"name": "岳麓山", "type": "山脉", "address": "岳麓区", "price": "免费", "tips": "登高望远，爱晚亭超美"},
            {"name": "五一广场", "type": "商业区", "address": "天心区", "price": "免费", "tips": "长沙最热闹的地方"},
        ],
        "美食约会": [
            {"name": "太平老街", "type": "美食街", "address": "天心区", "price": "¥50-100/人", "tips": "长沙小吃一条街"},
            {"name": "坡子街", "type": "美食街", "address": "天心区", "price": "¥50-150/人", "tips": "火宫殿所在地"},
            {"name": "超级文和友", "type": "网红店", "address": "天心区", "price": "¥100-200/人", "tips": "复古场景，超级出片"},
        ]
    },

    "厦门": {
        "户外约会": [
            {"name": "鼓浪屿", "type": "岛屿", "address": "思明区", "price": "¥35(船票)", "tips": "世界遗产，文艺小岛"},
            {"name": "厦门大学", "type": "校园", "address": "思明区", "price": "免费", "tips": "中国最美大学之一"},
            {"name": "环岛路", "type": "海滨", "address": "思明区", "price": "免费", "tips": "海边骑行，看日出日落"},
            {"name": "曾厝垵", "type": "文创村", "address": "思明区", "price": "免费", "tips": "文艺小吃村"},
        ],
        "美食约会": [
            {"name": "中山路步行街", "type": "商业街", "address": "思明区", "price": "¥50-150/人", "tips": "骑楼建筑，南洋风情"},
            {"name": "沙坡尾", "type": "文创区", "address": "思明区", "price": "¥50-150/人", "tips": "老渔港改造，文艺清新"},
        ]
    },

    "天津": {
        "室内约会": [
            {"name": "天津博物馆", "type": "博物馆", "address": "河西区", "price": "免费", "tips": "了解天津历史"},
            {"name": "滨海图书馆", "type": "图书馆", "address": "滨海新区", "price": "免费", "tips": "网红图书馆，超震撼"},
        ],
        "户外约会": [
            {"name": "五大道", "type": "历史街区", "address": "和平区", "price": "免费", "tips": "万国建筑博览"},
            {"name": "天津之眼", "type": "摩天轮", "address": "河北区", "price": "¥70", "tips": "俯瞰海河夜景"},
            {"name": "意大利风情街", "type": "风情街", "address": "河北区", "price": "免费", "tips": "假装在欧洲"},
        ],
        "美食约会": [
            {"name": "古文化街", "type": "美食街", "address": "南开区", "price": "¥50-100/人", "tips": "天津特色小吃"},
            {"name": "南市食品街", "type": "美食街", "address": "和平区", "price": "¥50-150/人", "tips": "老字号云集"},
        ]
    },

    "青岛": {
        "户外约会": [
            {"name": "栈桥", "type": "景点", "address": "市南区", "price": "免费", "tips": "青岛地标，看海好地方"},
            {"name": "八大关", "type": "风景区", "address": "市南区", "price": "免费", "tips": "万国建筑，拍照圣地"},
            {"name": "崂山", "type": "山脉", "address": "崂山区", "price": "¥130", "tips": "道教名山，风景超美"},
            {"name": "五四广场", "type": "广场", "address": "市南区", "price": "免费", "tips": "灯光秀超震撼"},
        ],
        "美食约会": [
            {"name": "劈柴院", "type": "美食街", "address": "市南区", "price": "¥50-100/人", "tips": "青岛老字号小吃街"},
            {"name": "台东步行街", "type": "商业街", "address": "市北区", "price": "¥50-150/人", "tips": "年轻人聚集地"},
        ]
    },

    # ============================================
    # 通用约会类型（全国适用）
    # ============================================
    "通用": {
        "活动体验": [
            {"name": "密室逃脱", "type": "解谜游戏", "price": "¥88-158/人", "tips": "2-8人，需要合作破冰"},
            {"name": "剧本杀", "type": "角色扮演", "price": "¥88-200/人", "tips": "6人以上，沉浸式体验"},
            {"name": "陶艺体验", "type": "手作", "price": "¥150-300/两人", "tips": "做陶瓷，作品可带走"},
            {"name": "烘焙DIY", "type": "手作", "price": "¥200-400/两人", "tips": "做蛋糕/饼干，超甜蜜"},
            {"name": "画室体验", "type": "手作", "price": "¥150-250/两人", "tips": "零基础油画，画完带走"},
            {"name": "木工体验", "type": "手作", "price": "¥200-400/两人", "tips": "做小家具/摆件"},
            {"name": "银饰DIY", "type": "手作", "price": "¥200-500/两人", "tips": "做戒指/手链，超有意义"},
            {"name": "陶艺拉坯", "type": "手作", "price": "¥100-200/人", "tips": "体验传统陶艺"},
            {"name": "皮具制作", "type": "手作", "price": "¥200-400/人", "tips": "做钱包/卡包"},
            {"name": "插花体验", "type": "手作", "price": "¥150-300/人", "tips": "花艺沙龙，超文艺"},
            {"name": "香薰蜡烛", "type": "手作", "price": "¥100-200/人", "tips": "做香薰蜡烛，超治愈"},
            {"name": "口红制作", "type": "手作", "price": "¥200-400/人", "tips": "做专属口红"},
        ],
        "运动娱乐": [
            {"name": "卡丁车", "type": "赛车", "price": "¥100-200/人", "tips": "速度与激情，心跳加速"},
            {"name": "真人CS", "type": "军事体验", "price": "¥100-200/人", "tips": "释放压力，玩得尽兴"},
            {"name": "射箭馆", "type": "运动", "price": "¥60-150/人", "tips": "超火的室内射箭"},
            {"name": "保龄球", "type": "运动", "price": "¥50-100/人", "tips": "老少皆宜，好上手"},
            {"name": "壁球/网球", "type": "运动", "price": "¥80-200/小时", "tips": "情侣对战首选"},
            {"name": "室内滑雪", "type": "运动", "price": "¥150-300/人", "tips": "不用去东北也能滑雪"},
            {"name": "蹦床公园", "type": "娱乐", "price": "¥100-200/人", "tips": "网红蹦床，超级解压"},
            {"name": "攀岩馆", "type": "运动", "price": "¥80-150/人", "tips": "室内攀岩，挑战自我"},
            {"name": "溜冰场", "type": "运动", "price": "¥50-100/人", "tips": "旱冰/真冰都可以"},
            {"name": "高尔夫练习场", "type": "运动", "price": "¥100-300/人", "tips": "体验贵族运动"},
        ],
        "休闲娱乐": [
            {"name": "电影院", "type": "观影", "price": "¥60-120/人", "tips": "经典约会选择"},
            {"name": "KTV", "type": "唱歌", "price": "¥50-150/人", "tips": "私密包间，尽情嗨唱"},
            {"name": "私人影院", "type": "观影", "price": "¥100-300/包", "tips": "情侣包间，更私密"},
            {"name": "电竞酒店", "type": "娱乐", "price": "¥200-500/间", "tips": "一起开黑打游戏"},
            {"name": "VR体验馆", "type": "科技", "price": "¥100-300/人", "tips": "沉浸式VR游戏"},
            {"name": "抓娃娃机", "type": "娱乐", "price": "¥20-100", "tips": "超火的网红娃娃机"},
            {"name": "猫咖/狗咖", "type": "休闲", "price": "¥50-80/人", "tips": "撸猫撸狗，超治愈"},
            {"name": "桌游吧", "type": "娱乐", "price": "¥30-60/人", "tips": "桌游种类超多"},
        ],
        "亲近自然": [
            {"name": "海边/沙滩", "type": "户外", "price": "免费-¥50", "tips": "海边散步，看日出日落"},
            {"name": "爬山/登山", "type": "户外", "price": "免费-¥50", "tips": "锻炼身体，呼吸新鲜空气"},
            {"name": "公园野餐", "type": "户外", "price": "¥50-100", "tips": "带零食饮料，超级惬意"},
            {"name": "湖泊划船", "type": "户外", "price": "¥30-80/船", "tips": "浪漫小船超有氛围"},
            {"name": "植物园/花展", "type": "户外", "price": "¥10-50", "tips": "赏花拍照，呼吸芬芳"},
            {"name": "动物园", "type": "户外", "price": "¥50-150", "tips": "看萌宠，超治愈"},
            {"name": "采摘园", "type": "户外", "price": "¥50-100", "tips": "草莓/樱桃/橘子等"},
            {"name": "农家乐", "type": "户外", "price": "¥100-300", "tips": "钓鱼、烧烤、棋牌"},
        ],
        "文艺清新": [
            {"name": "博物馆/美术馆", "type": "文化", "price": "免费-¥50", "tips": "提升内涵，了解历史"},
            {"name": "书店/图书馆", "type": "文艺", "price": "免费", "tips": "安静看书，氛围超好"},
            {"name": "展览/展会", "type": "文化", "price": "¥30-100", "tips": "艺术展/动漫展/设计周"},
            {"name": "文创园/老街", "type": "文艺", "price": "免费", "tips": "拍照打卡，文艺小店"},
            {"name": "创意市集", "type": "市集", "price": "免费", "tips": "手工艺品，淘宝贝"},
            {"name": "livehouse/音乐会", "type": "音乐", "price": "¥100-300", "tips": "小型演唱会，超有氛围"},
            {"name": "相声/脱口秀", "type": "娱乐", "price": "¥80-300", "tips": "笑到肚子疼"},
            {"name": "天文馆/科技馆", "type": "科技", "price": "免费-¥50", "tips": "涨知识，适合遛娃"},
        ],
        "美食探索": [
            {"name": "网红餐厅", "type": "美食", "price": "¥100-300/人", "tips": "环境好，拍照好看"},
            {"name": "特色小吃街", "type": "美食", "price": "¥50-100/人", "tips": "地方特色小吃"},
            {"name": "下午茶", "type": "美食", "price": "¥60-150/人", "tips": "咖啡+甜点+拍照"},
            {"name": "自助餐", "type": "美食", "price": "¥100-300/人", "tips": "吃到饱，适合大胃王"},
            {"name": "日料/韩料", "type": "美食", "price": "¥100-300/人", "tips": "精致料理，约会首选"},
            {"name": "火锅", "type": "美食", "price": "¥80-200/人", "tips": "热气腾腾，超有氛围"},
            {"name": "烧烤/烤肉", "type": "美食", "price": "¥80-200/人", "tips": "边吃边聊，超开心"},
            {"name": "西餐/意餐", "type": "美食", "price": "¥150-400/人", "tips": "浪漫氛围，约会首选"},
            {"name": "甜品店", "type": "美食", "price": "¥30-80/人", "tips": "蛋糕+奶茶，超甜蜜"},
        ],
        "夜生活": [
            {"name": "清吧/小酒馆", "type": "酒吧", "price": "¥80-200", "tips": "安静喝酒，聊聊天"},
            {"name": "露天酒吧", "type": "酒吧", "price": "¥100-300", "tips": "看夜景，氛围感满分"},
            {"name": "夜市/夜游", "type": "夜市", "price": "¥50-100", "tips": "逛夜市，感受烟火气"},
            {"name": "温泉/汗蒸", "type": "休闲", "price": "¥100-300/人", "tips": "放松身心，超舒服"},
            {"name": "24小时书店", "type": "文艺", "price": "免费", "tips": "深夜读书，别样浪漫"},
            {"name": "夜场电影", "type": "观影", "price": "¥60-100/人", "tips": "午夜场电影，超浪漫"},
        ]
    }
}


def get_destinations(city: str = None, category: str = None) -> list:
    """
    获取地点列表

    Args:
        city: 城市名称，不填则返回通用类型
        category: 类别名称，如"室内约会"、"户外约会"等

    Returns:
        地点列表
    """
    results = []

    # 获取指定城市
    if city and city in DESTINATION_DATABASE:
        city_data = DESTINATION_DATABASE[city]
        if category:
            # 返回指定类别
            if category in city_data:
                results.extend(city_data[category])
        else:
            # 返回所有类别
            for cat_data in city_data.values():
                results.extend(cat_data)

    # 添加通用类型
    if "通用" in DESTINATION_DATABASE:
        if category:
            if category in DESTINATION_DATABASE["通用"]:
                results.extend(DESTINATION_DATABASE["通用"][category])
        else:
            for cat_data in DESTINATION_DATABASE["通用"].values():
                results.extend(cat_data)

    return results


def search_destinations(keyword: str, city: str = None, limit: int = 10) -> list:
    """
    根据关键词搜索地点

    Args:
        keyword: 搜索关键词
        city: 城市名称
        limit: 返回数量限制

    Returns:
        匹配的地点列表
    """
    results = []
    keyword_lower = keyword.lower()

    # 确定搜索范围
    cities_to_search = [city] if city in DESTINATION_DATABASE else list(DESTINATION_DATABASE.keys())

    for search_city in cities_to_search:
        if search_city == "通用":
            continue

        city_data = DESTINATION_DATABASE.get(search_city, {})

        for category, places in city_data.items():
            for place in places:
                # 匹配关键词
                text = f"{place['name']} {place['type']} {place.get('address', '')} {place.get('tips', '')}".lower()
                if keyword_lower in text:
                    place_copy = place.copy()
                    place_copy["city"] = search_city
                    place_copy["category"] = category
                    results.append(place_copy)

    # 搜索通用类型
    for category, places in DESTINATION_DATABASE.get("通用", {}).items():
        for place in places:
            text = f"{place['name']} {place['type']} {place.get('tips', '')}".lower()
            if keyword_lower in text:
                place_copy = place.copy()
                place_copy["city"] = "全国通用"
                place_copy["category"] = category
                results.append(place_copy)

    # 去重
    seen = set()
    unique_results = []
    for p in results:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique_results.append(p)

    return unique_results[:limit]


def get_all_categories() -> dict:
    """获取所有类别"""
    categories = {}
    for city, city_data in DESTINATION_DATABASE.items():
        if city != "通用":
            categories[city] = list(city_data.keys())
    categories["全国通用"] = list(DESTINATION_DATABASE["通用"].keys())
    return categories


def get_all_cities() -> list:
    """获取所有城市"""
    return [city for city in DESTINATION_DATABASE.keys() if city != "通用"]
