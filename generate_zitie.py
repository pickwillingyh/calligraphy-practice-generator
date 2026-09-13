import os
import requests
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from reportlab.lib.pagesizes import A4 as a4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------------------------------------------------------------
# 1. 字体配置与自动下载逻辑
# -------------------------------------------------------------------------
FONT_PATH = "XingKai_Font.ttf"
FONT_NAME = "XingKai"

# 多个行楷/手写体字体下载源（如果某个链接失效，会自动尝试下一个）
FONT_URLS = [
    # 小米字体（可能失效）
    "https://font.sec.miui.com/font/MiSans_SuSheng/MiSans-SuSheng.ttf",
    # 备用字体源1 - 思源宋体（开源免费）
    "https://github.com/adobe-fonts/source-han-serif/raw/release/SubsetTTF/SourceHanSerifSC-Regular.ttf",
    # 备用字体源2 - 站酷字体（开源免费）
    "https://github.com/wordshub/free-font/raw/master/fonts/%E7%AB%99%E9%85%B7%E4%BC%91%E5%81%87%E4%BD%93.ttf",
]

def check_and_download_font():
    """检查并自动下载行书/手写体风格字体"""
    if not os.path.exists(FONT_PATH):
        print("正在查找可用的行楷字体...")

        # 首先检查本地是否有其他.ttf字体文件可用
        local_fonts = [f for f in os.listdir(".") if f.lower().endswith(".ttf") or f.lower().endswith(".ttc")]
        if local_fonts:
            print(f"发现本地字体文件: {local_fonts[0]}")
            try:
                os.rename(local_fonts[0], FONT_PATH)
                print(f"已重命名为: {FONT_PATH}")
                return True
            except:
                pass

        # 尝试多个下载源
        for i, font_url in enumerate(FONT_URLS):
            print(f"尝试字体源 {i+1}/{len(FONT_URLS)}: {font_url}")
            try:
                response = requests.get(font_url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                print(f"正在下载字体 ({total_size//1024}KB)，请耐心等待...")

                with open(FONT_PATH, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0 and downloaded % (1024*100) < 8192:  # 每100KB打印一次进度
                                percent = downloaded * 100 // total_size
                                print(f"下载进度: {percent}%", end="\r")

                print("\n字体下载成功！")
                return True

            except Exception as e:
                print(f"字体源 {i+1} 失败: {e}")
                continue

        print("所有在线字体源均不可用。")
        print("请手动执行以下操作之一：")
        print("1. 下载任意 .ttf 格式的行楷字体")
        print("2. 重命名为 'XingKai_Font.ttf'")
        print("3. 放置到当前目录下")
        print("")
        print("推荐字体下载网站：")
        print("- 字体天下: https://www.fonts.net.cn")
        print("- 站酷字体: https://www.zcool.com.cn/font")
        print("- 思源字体: https://source.typekit.com")
        return False

    return True

def register_system_font():
    """尝试注册系统中文字体，优先寻找行楷/书法字体"""
    import sys

    if sys.platform.startswith('win'):
        # Windows 系统字体路径
        fonts_dir = "C:\\Windows\\Fonts\\"

        # 优先寻找行楷/书法风格字体
        preferred_fonts = [
            # 华文行楷（Windows常见书法字体）
            ("STXingkai", "STXINGKA.TTF"),  # 华文行楷
            ("STKaiti", "STKAITI.TTF"),     # 华文楷体
            ("FZShuTi", "FZSTK.TTF"),       # 方正舒体（手写风格）
            ("FZYaoti", "FZYTK.TTF"),       # 方正姚体
            ("LiSu", "SIMLI.TTF"),          # 隶书
            ("YouYuan", "SIMYOU.TTF"),      # 幼圆
            ("KaiTi", "SIMKAI.TTF"),        # 楷体
        ]

        # 首先尝试书法字体
        for font_name, font_file in preferred_fonts:
            font_path = fonts_dir + font_file
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"成功注册书法字体: {font_name} ({font_file})")
                    print(f"这是行楷/手写风格的字体，适合字帖使用！")
                    return font_name
                except Exception as e:
                    print(f"注册书法字体 {font_name} 失败: {e}")
                    continue

        # 如果找不到书法字体，尝试其他系统字体
        backup_fonts = {
            "Microsoft YaHei": "msyh.ttc",  # 微软雅黑
            "SimSun": "simsun.ttc",         # 宋体
            "NSimSun": "simsun.ttc",        # 新宋体
            "FangSong": "simfang.ttf",      # 仿宋
        }

        for font_name, font_file in backup_fonts.items():
            font_path = fonts_dir + font_file
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"成功注册系统字体: {font_name}")
                    print(f"注意: 这不是专门的书法字体，效果可能不如行楷字体美观")
                    return font_name
                except Exception as e:
                    print(f"注册字体 {font_name} 失败: {e}")
                    continue

    print("警告: 未找到系统中文字体，将使用Helvetica（可能无法显示中文）")
    print("强烈建议手动下载行楷字体文件！")
    return "Helvetica"

def setup_font():
    """
    设置字体：优先使用系统自带的华文行楷字体，
    如果找不到则尝试其他书法字体，
    最后尝试下载字体。
    """
    # 首先检查系统自带的华文行楷字体
    print("正在查找系统行楷字体...")

    # 尝试直接使用系统华文行楷字体
    system_font_name = register_system_font()

    if system_font_name != "Helvetica":
        # 如果成功找到系统字体，直接使用它
        print(f"✓ 已选择系统字体: {system_font_name}")
        return system_font_name

    # 如果系统字体不可用，尝试下载
    print("系统字体不可用，尝试下载行楷字体...")
    if check_and_download_font():
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
            print(f"✓ 已使用下载的字体: {FONT_NAME}")
            return FONT_NAME
        except Exception as e:
            print(f"注册下载字体失败: {e}")

    # 所有方法都失败，使用Helvetica
    print("⚠️ 所有字体获取方法均失败，使用Helvetica（可能无法显示中文）")
    return "Helvetica"

# 执行字体设置
FONT_NAME = setup_font()

# -------------------------------------------------------------------------
# 2. 完整的《道德经》八十一章数据
# -------------------------------------------------------------------------
daodejing_data = [
    {"title": "第一章", "content": ["道可道非常道名可名非常名", "无名天地之始有名万物之母", "故常无欲以观其妙常有欲以观其徼", "此两者同出而异名同谓之玄", "玄之又玄众妙之门"]},
    {"title": "第二章", "content": ["天下皆知美之为美斯恶已", "皆知善之为善斯不善已", "有无相生难易相成长短相形", "高下相倾音声相和前后相随", "是以圣人处无为之事行不言之教", "万物作焉而不辞生而不有", "为而不恃功成而弗居", "夫唯弗居是以不去"]},
    {"title": "第三章", "content": ["不尚贤使民不争", "不贵难得之货使民不盗", "不见可欲使民心不乱", "是以圣人之治虚其心实其腹", "弱其志强其骨常使民无知无欲", "使夫智者不敢为也为无为则无不治"]},
    {"title": "第四章", "content": ["道冲而用之或不盈", "渊兮似万物之宗", "挫其锐解其纷和其光同其尘", "湛兮似或存吾不知谁之子", "象帝之先"]},
    {"title": "第五章", "content": ["天地不仁以万物为刍狗", "圣人不仁以百姓为刍狗", "天地之间其犹橐龠乎", "虚而不屈动而愈出", "多言数穷不如守中"]},
    {"title": "第六章", "content": ["谷神不死是谓玄牝", "玄牝之门是谓天地根", "绵绵若存用之不勤"]},
    {"title": "第七章", "content": ["天长地久", "天地所以能长且久者", "以其不自生故能长生", "是以圣人后其身而身先", "外其身而身存", "非以其无私邪故能成其私"]},
    {"title": "第八章", "content": ["上善若水水善利万物而不争", "处众人之所恶故几于道", "居善地心善渊与善仁", "言善信正善治事善能动善时", "夫唯不争故无尤"]},
    {"title": "第九章", "content": ["持而盈之不如其已", "揣而锐之不可长保", "金玉满堂莫之能守", "富贵而骄自遗其咎", "功遂身退天之道"]},
    {"title": "第十章", "content": ["载营魄抱一能无离乎", "专气致柔能如婴儿乎", "涤除玄鉴能无疵乎", "爱国治民能无为乎", "天门开阖能为雌乎", "明白四达能无知乎", "生之畜之生而不有", "为而不恃长而不宰是谓玄德"]},
    {"title": "第十一章", "content": ["三十辐共一毂当其无有车之用", "埏埴以为器当其无有器之用", "凿户牖以为室当其无有室之用", "故有之以为利无之以为用"]},
    {"title": "第十二章", "content": ["五色令人目盲五音令人耳聋", "五味令人口爽驰骋畋猎", "令人心发狂难得之货令人行妨", "是以圣人为腹不为目", "故去彼取此"]},
    {"title": "第十三章", "content": ["宠辱若惊贵大患若身", "何谓宠辱若惊", "宠为下得之若惊失之若惊", "是谓宠辱若惊", "何谓贵大患若身", "吾所以有大患者为吾有身", "及吾无身吾有何患", "故贵以身为天下若可寄天下", "爱以身为天下若可托天下"]},
    {"title": "第十四章", "content": ["视之不见名曰夷听之不闻", "名曰希搏之不得名曰微", "此三者不可致诘故混而为一", "其上不皦其下不昧", "绳绳不可名复归于无物", "是谓无状之状无物之象", "是谓惚恍", "迎之不见其首随之不见其后", "执古之道以御今之有", "能知古始是谓道纪"]},
    {"title": "第十五章", "content": ["古之善为道者微妙玄通深不可识", "夫唯不可识故强为之容", "豫兮若冬涉川犹兮若畏四邻", "俨兮其若客涣兮若冰之将释", "敦兮其若朴旷兮其若谷", "混兮其若浊", "孰能浊以静之徐清", "孰能安以动之徐生", "保此道者不欲盈", "夫唯不盈故能蔽不新成"]},
    {"title": "第十六章", "content": ["致虚极守静笃万物并作", "吾以观复夫物芸芸各复归其根", "归根曰静是谓复命", "复命曰常知常曰明", "不知常妄作凶", "知常容容乃公公乃王", "王乃天天乃道道乃久", "没身不殆"]},
    {"title": "第十七章", "content": ["太上不知有之其次亲而誉之", "其次畏之其次侮之", "信不足焉有不信焉", "犹兮其贵言", "功成事遂百姓皆谓我自然"]},
    {"title": "第十八章", "content": ["大道废有仁义智慧出有大伪", "六亲不和有孝慈", "国家昏乱有忠臣"]},
    {"title": "第十九章", "content": ["绝圣弃智民利百倍", "绝仁弃义民复孝慈", "绝巧弃利盗贼无有", "此三者以为文不足", "故令有所属", "见素抱朴少私寡欲"]},
    {"title": "第二十章", "content": ["绝学无忧唯之与阿相去几何", "善之与恶相去若何", "人之所畏不可不畏", "荒兮其未央哉", "众人熙熙如享太牢如春登台", "我独泊兮其未兆如婴儿之未孩", "傒傒焉若无所归众人皆有余", "而我独若遗我愚人之心也哉", "沌沌兮俗人昭昭我独昏昏", "俗人察察我独闷闷", "澹兮其若海飂兮若无止", "众人皆有以而我独顽似鄙", "我独异于人而贵食母"]},
    {"title": "第二十一章", "content": ["孔德之容唯道是从", "道之为物唯恍唯惚", "惚兮恍兮其中有象", "恍兮惚兮其中有物", "窈兮冥兮其中有精", "其精甚真其中有信", "自古及今其名不去以阅众甫", "吾何以知众甫之状哉以此"]},
    {"title": "第二十二章", "content": ["曲则全枉则直洼则盈", "敝则新少则得多则惑", "是以圣人抱一为天下式", "不自见故明不自是故彰", "不自伐故有功不自矜故长", "夫唯不争故天下莫能与之争", "古之所谓曲则全者", "岂虚言哉诚全而归之"]},
    {"title": "第二十三章", "content": ["希言自然故飘风不终朝", "骤雨不终日孰为此者天地", "天地尚不能持久而况于人乎", "故从事于道者", "同于道者道亦乐得之", "同于德者德亦乐得之", "同于失者失亦乐得之", "信不足焉有不信焉"]},
    {"title": "第二十四章", "content": ["企者不立跨者不行", "自见者不明自是者不彰", "自伐者无功自矜者不长", "其在道也曰余食赘行", "物或恶之故有道者不处"]},
    {"title": "第二十五章", "content": ["有物混成先天地生", "寂兮寥兮独立而不改", "周行而不殆可以为天下母", "吾不知其名字之曰道", "强为之名曰大大曰逝", "逝曰远处远曰反", "故道大天大地大王亦大", "域中有四大而王居其一焉", "人法地地法天天法道道法自然"]},
    {"title": "第二十六章", "content": ["重为轻根静为躁君", "是以圣人终日行不离辎重", "虽有荣观燕处超然", "如何万乘之主而以身轻天下", "轻则失本躁则失君"]},
    {"title": "第二十七章", "content": ["善行无辙迹善言无瑕谪", "善数不用筹策", "善闭无关楗而不可开", "善结无绳约而不可解", "是以圣人常善救人故无弃人", "常善救物故无弃物是谓袭明", "故善人者不善人之师", "不善人者善人之资", "不贵其师不爱其资", "虽智大迷是谓要妙"]},
    {"title": "第二八章", "content": ["知其雄守其雌为天下溪", "为天下溪常德不离", "复归于婴儿", "知其白守其黑为天下式", "为天下式常德不忒", "复归于无极", "知其荣守其辱为天下谷", "为天下谷常德乃足", "复归于朴", "朴散则以为器圣人用之", "则为官长故大制不割"]},
    {"title": "第二十九章", "content": ["将欲取天下而为之吾见其不得已", "天下神器不可为也", "为者败之执者失之", "夫物或行或随或嘘或吹", "或强或羸或挫或隳", "是以圣人去甚去奢去泰"]},
    {"title": "第三十章", "content": ["以道佐人主者不以兵强天下", "其事好还师之所处荆棘生焉", "大军之后必有凶年", "善有果而已不敢以取强", "果而勿矜果而勿伐果而勿骄", "果而不得已果而勿强", "物壮则老是谓不道不道早已"]},
    {"title": "第三十一章", "content": ["夫佳兵者不祥之器物或恶之", "故有道者不处", "君子居则贵左用兵则贵右", "兵者不祥之器非君子之器", "不得已而用之恬淡为上", "胜而不美而美之者", "是乐杀人夫乐杀人者", "则不可得志于天下矣", "吉事尚左凶事尚右", "偏将军居左上将军居右", "言以丧礼处之杀人之众", "以哀悲泣之战胜以丧礼处之"]},
    {"title": "第三十二章", "content": ["道常无名朴虽小天下莫能臣也", "侯王若能守之万物将自宾", "天地相合以降甘露", "民莫之令而自均", "始制有名名亦既有", "夫亦将知止知止所以不殆", "譬道之在天下犹川谷之于江海"]},
    {"title": "第三十三章", "content": ["知人者智自知者明", "胜人者有力自胜者强", "知足者富强行者有志", "不失其所者久死而不亡者寿"]},
    {"title": "第三十四章", "content": ["大道泛兮其可左右", "万物恃之以生而不辞", "功成不名有爱养万物而不为主", "常无欲可名于小", "万物归焉而不为主可名为大", "以其终不自为大故能成其大"]},
    {"title": "第三十五章", "content": ["执大象天下往往而不害安平太", "乐与饵过客止", "道之出口淡乎其无味", "视之不足见听之不足闻", "用之不足既"]},
    {"title": "第三十六/章", "content": ["将欲歙之必固张之", "将欲弱之必固强之", "将欲废之必固兴之", "将欲取之必固与之", "是谓微明柔弱胜刚强", "鱼不可脱于渊", "国之利器不可以示人"]},
    {"title": "第三十七章", "content": ["道常无为而无不为", "侯王若能守之万物将自化", "化而欲作吾将镇之以无名之朴", "无名之朴亦将不欲", "不欲以静天下将自定"]},
    {"title": "第三八章", "content": ["上德不德是以有德", "下德不失德是以无德", "上德无为而无以为", "下德为之而有以为", "上仁为之而无以为", "上义为之而有以为", "上礼为之而莫之应", "则攘臂而扔之", "故失道而后德失德而后仁", "失仁而后义失义而后礼", "夫礼者忠信之薄而乱之首", "前识者道之华而愚之始", "是以大丈夫处其厚不居其薄", "处其实不居其华故去彼取此"]},
    {"title": "第三十九章", "content": ["昔之得一者天得一以清", "地得一以宁神得一以灵", "谷得一以盈万物得一以生", "侯王得一以为天下贞其致之", "天无以清将恐裂地无以宁", "将恐废神无以灵将恐歇", "谷无以盈将恐竭万物无以生", "将恐灭侯王无以贵高将恐蹶", "故贵以贱为本高以下为基", "是以侯王自谓孤寡不毂", "此非以贱为本邪非乎", "故致数舆无舆不欲琭琭如玉", "珞珞如石"]},
    {"title": "第四十章", "content": ["反者道之动弱者道之用", "天下万物生于有有生于无"]},
    {"title": "第四十一章", "content": ["上士闻道勤而行之中士闻道", "若存若亡下士闻道大笑之", "不笑不足以为道", "故建言有之明道若昧", "进道若退夷道若类", "上德若谷大白若辱", "广德若不足建德若偷", "质真若渝大方无隅", "大器晚成大音希声", "大象无形道隐无名", "夫唯道善贷且成"]},
    {"title": "第四十二章", "content": ["道生一一生二二生三", "三生万物万物负阴而抱阳", "冲气以为和", "人之所恶唯孤寡不毂", "而王公以为称", "故物或损之而益或益之而损", "人之所教我亦教之", "强梁者不得其死吾将以为教父"]},
    {"title": "第四十三章", "content": ["天下之至柔驰骋天下之至坚", "无有入无间吾是以知无为之有益", "不言之教无为之益天下希及之"]},
    {"title": "第四十四章", "content": ["名与身孰亲身与货孰多", "得与亡孰病", "是故甚爱必大费多藏必厚亡", "知足不辱知止不殆可以长久"]},
    {"title": "第四十五章", "content": ["大成若缺其用不弊", "大盈若冲其用不穷", "大直若屈大巧若拙大辩若讷", "躁胜寒静胜热清静为天下正"]},
    {"title": "第四十六章", "content": ["天下有道却走马以粪", "天下无道戎马生于郊", "祸莫大于不知足", "咎莫大于欲得", "故知足之足常足矣"]},
    {"title": "第四十七章", "content": ["不出户知天下不窥牖见天道", "其出弥远其知弥少", "是以圣人不行而知不见而名", "不为而成"]},
    {"title": "第四八章", "content": ["为学日益为道日损", "损之又损以至于无为", "无为而无不为", "取天下常以无事", "及其有事不足以取天下"]},
    {"title": "第四十九章", "content": ["圣人常无心以百姓心为心", "善者吾善之不善者吾亦善之", "德善信者吾信之不信者吾亦信之", "德信圣人在天下怵怵", "为天下浑其心", "百姓皆注其耳目圣人皆孩之"]},
    {"title": "第五十章", "content": ["出生入死生之徒十有三", "死之徒十有三", "人之生动之死地亦十有三", "夫何故以其生生之厚", "闻善摄生者陆行不遇兕虎", "入军不披甲兵兕无所投其角", "虎无所措其爪兵无所容其刃", "夫何故以其无死地"]},
    {"title": "第五十一章", "content": ["道生之德畜之物形之势成之", "是以万物莫不尊道而贵德", "道之尊德之贵夫莫之命而常自然", "故道生之德畜之", "长之育之亭之毒之养之覆之", "生而不有为而不恃", "长而不宰是谓玄德"]},
    {"title": "第五十二章", "content": ["天下有始以为天下母", "既得其母以知其子", "既知其子复守其母没身不殆", "塞其兑闭其门终身不勤", "开其兑济其事ext终身不救", "见小曰明守柔曰强", "用其光复归其明无遗身殃", "是谓袭常"]},
    {"title": "第五十三章", "content": ["使我介然有知行于大道唯施是畏", "大道甚夷而人好径", "朝甚除田甚芜仓甚虚", "服文采带利剑厌饮食财货有余", "是谓盗夸非道也哉"]},
    {"title": "第五十四章", "content": ["善建者不拔善抱者不脱", "子孙以祭祀不辍", "修之于身其德乃真修之于家", "其德乃余修之于乡其德乃长", "修之于邦其德乃丰修之于天下", "其德乃普故以身观身以家观家", "以乡观乡以邦观邦", "以天下观天下吾何以知天下然哉", "以此"]},
    {"title": "第五十五章", "content": ["含德之厚比于赤子", "毒虫不螫猛兽不据攫鸟不搏", "骨弱筋柔而握固", "未知牝牡之合而朘作精之至也", "终日号而不嗄和之至也", "知和曰常知常曰明益生曰祥", "心使气曰强物壮则老", "谓之不道不道早已"]},
    {"title": "第五十六章", "content": ["知者不言言者不知", "塞其兑闭其门挫其锐解其纷", "和其光同其尘是谓玄同", "故不可得而亲不可得而疏", "不可得而利不可得而害", "不可得而贵不可得而贱", "故为天下贵"]},
    {"title": "第五十七章", "content": ["以正治国以奇用兵以无事取天下", "吾何以知其然哉以此", "天下多忌讳而民弥贫", "民多利器国家滋昏", "人多技巧奇物滋起", "法令滋彰盗贼多有", "故圣人云我无为而民自化", "我好静而民自正我无事而民自富", "我无欲而民自朴"]},
    {"title": "第五十八章", "content": ["其政闷闷其民淳淳", "其政察察其民缺缺", "祸兮福之所倚福兮祸之所伏", "孰知其极其无正", "正复为奇善复为妖", "人之迷其日固久", "是以圣人方而不割廉而不刿", "直而不肆光而不耀"]},
    {"title": "第五十九章", "content": ["治人事天莫若啬", "夫唯啬是谓早服", "早服谓之重积德", "重积德则无不克", "无不克则莫知其极", "莫知其极可以有国", "有国之母可以长久", "是谓深根固柢长生久视之道"]},
    {"title": "第六十章", "content": ["治大国若烹小鲜", "以道莅天下其鬼不神", "非其鬼不神其神不伤人", "非其神不伤人圣人亦不伤人", "夫两不相伤故德交归焉"]},
    {"title": "第六十一章", "content": ["大邦者下流天下之交天下之牝", "牝常以静胜牡以静为下", "故大邦以下小邦则取小邦", "小邦以下大邦则取大邦", "故或下以取或下而取", "大邦不过欲兼畜人", "小邦不过欲入事人", "夫两者各得其所欲大者宜为下"]},
    {"title": "第六十二章", "content": ["道者万物之奥善人之宝", "不善人之所保", "美言可以市尊行可以加人", "人之不善何弃之有", "故立天子置三公", "虽有拱璧以策先马", "不如坐进此道", "古之所以贵此道者何", "不曰以求得有罪以免邪", "故为天下贵"]},
    {"title": "第六十三章", "content": ["为无为事无事味无味", "大小多少报怨以德", "图难于其易为大于其细", "天下难事必作于易", "天下大事必作于细", "是以圣人终不为大故能成其大", "夫轻诺必寡信多难必多易", "是以圣人犹难之故终无难矣"]},
    {"title": "第六十四章", "content": ["其安易持其未兆易谋", "其脆易泮其微易散", "为之于未有治之于未乱", "合抱之木生于毫末", "九层之台起于累土", "千里之行始于足下", "为者败之执者失之", "是以圣人无为故无败", "无执故无失", "民之从事常于几成而败之", "慎终如始则无败事", "是以圣人欲不欲不贵难得之货", "学不学复众人之所过", "以辅万物之自然而不敢为"]},
    {"title": "第六十五章", "content": ["古之善为道者非以明民", "将以愚之民之难治以其智多", "故以智治国国之贼", "不以智治国国之福", "知此两者亦稽式", "常知稽式是谓玄德", "玄德深矣远矣与物反矣", "然后乃至大顺"]},
    {"title": "第六十六/章", "content": ["江海所以能为百谷王者", "以其善下之故能为百谷王", "是以欲上民必以言下之", "欲先民必以身后之", "是以圣人处上而民不重", "处前而民不害", "是以天下乐推而不厌", "以其不争故天下莫能与之争"]},
    {"title": "第六十七章", "content": ["天下皆谓我大似不肖", "夫唯大故似不肖若肖久矣其细也夫", "我有三宝持而保之", "一曰慈二曰俭", "三曰不敢为天下先", "慈故能勇俭故能广", "不敢为天下先故能成器长", "今舍慈且勇舍俭且广", "舍后且先死矣", "夫慈以战则胜以守则固", "天将救之以慈卫之"]},
    {"title": "第六十八章", "content": ["善为士者不武善战者不怒", "善胜敌者不与善用人者为之下", "is谓不争之德是谓用人之力", "是谓配天古之极"]},
    {"title": "第六十九章", "content": ["用兵有言吾不敢为主而为客", "不敢进寸而退尺", "是谓行无行攘无臂", "扔无敌执无兵", "祸莫大于轻敌轻敌几丧吾宝", "故抗兵相若哀者胜矣"]},
    {"title": "第七十章", "content": ["吾言甚易知甚易行", "天下莫能知莫能行", "言有宗事有君夫唯无知", "是以不我知知我者希", "则我者贵是以圣人被褐怀玉"]},
    {"title": "第七十一章", "content": ["知不知上不知知病", "圣人不病以其病病", "夫唯病病是以不病"]},
    {"title": "第七十二章", "content": ["民不畏威则大威至", "无狎其所居无厌其所生", "夫唯不厌是以不厌", "是以圣人自知不自见", "自爱不自贵故去彼取此"]},
    {"title": "第七十三章", "content": ["勇于敢则杀勇于不敢则活", "此两者或利或害", "天之所恶孰知其故", "是以圣人犹难之", "天之道不争而善胜不言而善应", "不召而自来繟然而善谋", "天网恢恢疏而不失"]},
    {"title": "第七十四章", "content": ["民不畏死奈何以死惧之", "若使民常畏死而为奇者", "吾得执而杀之孰敢", "常有司杀者杀夫代司杀者杀", "是谓代大匠斫", "夫代大匠斫者希有不伤其手矣"]},
    {"title": "第七十五章", "content": ["民之饥以其上食税之多是以饥", "民之难治以其上之有为", "是以难治民之轻死", "以其上求生之厚是以轻死", "夫唯无以生为者是贤于贵生"]},
    {"title": "第七十六/章", "content": ["人之生也柔弱其死也坚强", "万物草木之生也柔脆其死也枯槁", "故坚强者死之徒柔弱者生之徒", "是以兵强则灭木强则折", "强大处下柔弱处上"]},
    {"title": "第七十七章", "content": ["天之道其犹张弓舆高者抑之", "下者举之有余者损之", "不足者补之天之道", "损有余而补不足", "人之道则不然损不足以奉有余", "孰能有余以奉天下唯有道者", "是以圣人为而不恃功成而不居", "其不欲见贤"]},
    {"title": "第七十八章", "content": ["天下莫柔弱于水", "而攻坚强者莫之能胜以其无以易之", "弱之胜强柔之胜刚", "天下莫不知莫能行", "是以圣人云受国之垢", "是谓社稷主受国不祥是为天下王", "正言若反"]},
    {"title": "第七十九章", "content": ["和大怨必有余怨安可以为善", "是以圣人执左契而不责于人", "有德司契无德司彻", "天道无亲常与善人"]},
    {"title": "第八十章", "content": ["小国寡民使有什伯之器而不用", "使民重死而不远徙", "虽有舟舆无所乘之", "虽有甲兵无所陈之", "使民复结绳而用之", "甘其食美其服安其居乐其俗", "邻国相望鸡犬之声相闻", "民至老死不相往来"]},
    {"title": "第八十一章", "content": ["信言不美美言不信", "善者不辩辩者不善", "知者不博博者不知", "圣人不积既以为人己愈有", "既以予人己愈多", "天之道利而不害圣人之道为而不争"]}
]

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 10)  # 稍微增大页码字体
        self.setFillColor(colors.HexColor('#666666'))
        page_text = f"第 {self._pageNumber} 页  /  共 {page_count} 页"
        self.drawCentredString(595.27 / 2, 30, page_text)  # 提高页码位置
        self.restoreState()

def draw_mi_zi_ge(canvas_obj, x, y, size):
    canvas_obj.setStrokeColor(colors.HexColor('#FFAAAA'))
    canvas_obj.setLineWidth(1.2)  # 格子变大，线条加粗
    canvas_obj.rect(x, y, size, size, stroke=1, fill=0)

    canvas_obj.setLineWidth(0.6)  # 内部线条加粗
    canvas_obj.setDash(2, 2)
    canvas_obj.line(x + size/2, y, x + size/2, y + size)
    canvas_obj.line(x, y + size/2, x + size, y + size/2)
    canvas_obj.line(x, y, x + size, y + size)
    canvas_obj.line(x, y + size, x + size, y)
    canvas_obj.setDash()

def generate_full_pdf(filename="daodejing_full_calligraphy.pdf"):
    page_width, page_height = a4
    c = NumberedCanvas(filename, pagesize=a4)

    # 目标：打印后格子大小约2cm×2cm
    # 2cm ≈ 57点 (1点=1/72英寸≈0.3528mm, 20mm/0.3528≈57点)
    margin_left = 35  # 边距减小
    margin_top = 45   # 上边距减小
    grid_size = 57    # 2cm打印大小
    grid_gap = 3
    row_gap = 12      # 行间距减小

    current_y = page_height - margin_top

    for chapter in daodejing_data:
        if current_y - (20 + grid_size * 2 + row_gap) < margin_top:
            c.showPage()
            current_y = page_height - margin_top

        if FONT_NAME != "Helvetica":
            c.setFont(FONT_NAME, 14)  # 章节标题字体
            c.setFillColor(colors.HexColor('#333333'))
            c.drawString(margin_left, current_y - 12, f"■ {chapter['title']}")
            current_y -= 20

        # 将本章所有内容用中文逗号连接起来
        # 例如：["句子1", "句子2"] → "句子1，句子2"
        combined_text = "，".join(chapter['content'])

        # 计算每行最大字数
        max_chars_per_line = int((page_width - 2 * margin_left) / (grid_size + grid_gap))
        print(f"章节 {chapter['title']}: 每行最多 {max_chars_per_line} 个字")
        sys.stdout.flush()

        # 按最大字数分割长文本
        lines = []
        text_to_split = combined_text
        max_iterations = 100
        iteration = 0
        while text_to_split and iteration < max_iterations:
            iteration += 1
            if len(text_to_split) <= max_chars_per_line:
                lines.append(text_to_split)
                break
            else:
                # 尽量在逗号处分割，如果没有逗号则按最大字数硬分割
                split_pos = max_chars_per_line
                # 向前查找逗号
                for i in range(max_chars_per_line, 0, -1):
                    if text_to_split[i] == '，':
                        split_pos = i + 1  # 包含逗号
                        break
                lines.append(text_to_split[:split_pos])
                text_to_split = text_to_split[split_pos:]
                # 如果分割后剩余部分以逗号开头，去掉逗号
                if text_to_split.startswith('，'):
                    text_to_split = text_to_split[1:]
        if iteration >= max_iterations:
            print(f"警告：章节 {chapter['title']} 文本分割可能陷入无限循环")

        for line_text in lines:
            needed_height = (grid_size * 2) + row_gap
            if current_y - needed_height < margin_top:
                c.showPage()
                current_y = page_height - margin_top

            x_pos = margin_left
            y_pos_row1 = current_y - grid_size

            for char in line_text:
                draw_mi_zi_ge(c, x_pos, y_pos_row1, grid_size)
                if FONT_NAME != "Helvetica":
                    c.setFont(FONT_NAME, grid_size * 0.68)  # 字体大小为格子的68%
                    c.setFillColor(colors.HexColor('#B0B0B0'))

                    char_width = c.stringWidth(char, FONT_NAME, grid_size * 0.68)
                    text_x = x_pos + (grid_size - char_width) / 2
                    text_y = y_pos_row1 + (grid_size * 0.20)  # 调整垂直位置
                    c.drawString(text_x, text_y, char)
                x_pos += grid_size + grid_gap

            x_pos = margin_left
            y_pos_row2 = y_pos_row1 - grid_size
            for _ in line_text:
                draw_mi_zi_ge(c, x_pos, y_pos_row2, grid_size)
                x_pos += grid_size + grid_gap

            current_y = y_pos_row2 - row_gap

        # 章节结束后，如果页面还有空间，填充空白田字格
        # 计算一行田字格所需的高度
        needed_height = (grid_size * 2) + row_gap
        while current_y - needed_height >= margin_top:
            # 填充一行空白田字格
            x_pos = margin_left
            y_pos_row1 = current_y - grid_size
            y_pos_row2 = y_pos_row1 - grid_size

            # 绘制空白田字格（没有文字）
            for _ in range(max_chars_per_line):
                draw_mi_zi_ge(c, x_pos, y_pos_row1, grid_size)
                draw_mi_zi_ge(c, x_pos, y_pos_row2, grid_size)
                x_pos += grid_size + grid_gap

            current_y = y_pos_row2 - row_gap

        # 章节间距减小
        current_y -= 8  # 章节间距减小

    c.save()
    print(f"成功：{filename}")

def generate_full_pdf_1_5cm(filename="daodejing_full_calligraphy_1_5cm.pdf"):
    """生成1.5cm格子版本"""
    page_width, page_height = a4
    c = NumberedCanvas(filename, pagesize=a4)

    # 目标：打印后格子大小约1.5cm×1.5cm
    # 1.5cm ≈ 43点 (1点=1/72英寸≈0.3528mm, 15mm/0.3528≈43点)
    margin_left = 35  # 边距
    margin_top = 45   # 上边距
    grid_size = 43    # 1.5cm打印大小
    grid_gap = 3
    row_gap = 12      # 行间距

    current_y = page_height - margin_top

    for chapter in daodejing_data:
        if current_y - (20 + grid_size * 2 + row_gap) < margin_top:
            c.showPage()
            current_y = page_height - margin_top

        if FONT_NAME != "Helvetica":
            c.setFont(FONT_NAME, 14)  # 章节标题字体
            c.setFillColor(colors.HexColor('#333333'))
            c.drawString(margin_left, current_y - 12, f"■ {chapter['title']}")
            current_y -= 20

        # 将本章所有内容用中文逗号连接起来
        combined_text = "，".join(chapter['content'])

        # 计算每行最大字数
        max_chars_per_line = int((page_width - 2 * margin_left) / (grid_size + grid_gap))
        print(f"1.5cm版本 章节 {chapter['title']}: 每行最多 {max_chars_per_line} 个字")

        # 按最大字数分割长文本
        lines = []
        text_to_split = combined_text
        max_iterations = 100
        iteration = 0
        while text_to_split and iteration < max_iterations:
            iteration += 1
            if len(text_to_split) <= max_chars_per_line:
                lines.append(text_to_split)
                break
            else:
                # 尽量在逗号处分割，如果没有逗号则按最大字数硬分割
                split_pos = max_chars_per_line
                # 向前查找逗号
                for i in range(max_chars_per_line, 0, -1):
                    if text_to_split[i] == '，':
                        split_pos = i + 1  # 包含逗号
                        break
                lines.append(text_to_split[:split_pos])
                text_to_split = text_to_split[split_pos:]
                # 如果分割后剩余部分以逗号开头，去掉逗号
                if text_to_split.startswith('，'):
                    text_to_split = text_to_split[1:]
        if iteration >= max_iterations:
            print(f"警告：章节 {chapter['title']} 文本分割可能陷入无限循环")

        for line_text in lines:
            needed_height = (grid_size * 2) + row_gap
            if current_y - needed_height < margin_top:
                c.showPage()
                current_y = page_height - margin_top

            x_pos = margin_left
            y_pos_row1 = current_y - grid_size

            for char in line_text:
                draw_mi_zi_ge(c, x_pos, y_pos_row1, grid_size)
                if FONT_NAME != "Helvetica":
                    c.setFont(FONT_NAME, grid_size * 0.68)  # 字体大小为格子的68%
                    c.setFillColor(colors.HexColor('#B0B0B0'))

                    char_width = c.stringWidth(char, FONT_NAME, grid_size * 0.68)
                    text_x = x_pos + (grid_size - char_width) / 2
                    text_y = y_pos_row1 + (grid_size * 0.20)  # 调整垂直位置
                    c.drawString(text_x, text_y, char)
                x_pos += grid_size + grid_gap

            x_pos = margin_left
            y_pos_row2 = y_pos_row1 - grid_size
            for _ in line_text:
                draw_mi_zi_ge(c, x_pos, y_pos_row2, grid_size)
                x_pos += grid_size + grid_gap

            current_y = y_pos_row2 - row_gap

        # 章节结束后，如果页面还有空间，填充空白田字格
        # 计算一行田字格所需的高度
        needed_height = (grid_size * 2) + row_gap
        while current_y - needed_height >= margin_top:
            # 填充一行空白田字格
            x_pos = margin_left
            y_pos_row1 = current_y - grid_size
            y_pos_row2 = y_pos_row1 - grid_size

            # 绘制空白田字格（没有文字）
            for _ in range(max_chars_per_line):
                draw_mi_zi_ge(c, x_pos, y_pos_row1, grid_size)
                draw_mi_zi_ge(c, x_pos, y_pos_row2, grid_size)
                x_pos += grid_size + grid_gap

            current_y = y_pos_row2 - row_gap

        # 章节间距减小
        current_y -= 8  # 章节间距减小

    c.save()
    print(f"成功生成1.5cm版本：{filename}")

if __name__ == "__main__":
    print("开始生成《道德经》字帖...")
    print("=" * 50)

    # 生成2cm格子版本
    print("\n【1/2】生成2cm格子版本...")
    generate_full_pdf()

    # 生成1.5cm格子版本
    print("\n【2/2】生成1.5cm格子版本...")
    generate_full_pdf_1_5cm()

    print("\n" + "=" * 50)
    print("所有版本生成完成！")
    print("请查看当前目录下的PDF文件：")
    print("- daodejing_full_calligraphy.pdf (2cm格子)")
    print("- daodejing_full_calligraphy_1_5cm.pdf (1.5cm格子)")
